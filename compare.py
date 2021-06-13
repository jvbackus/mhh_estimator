import os
import joblib
import awkward as ak
import numpy as np
from keras.models import load_model
from argparse import ArgumentParser
from bbtautau import log; log = log.getChild('compare')

if __name__ == '__main__':

    parser = ArgumentParser()
    parser.add_argument('--debug', default=False, action='store_true')
    parser.add_argument('--scikit', default='latest_scikit.clf')
    parser.add_argument('--keras', default='latest_keras.h5')
    parser.add_argument('--include-mmc', default=False, action='store_true')
    parser.add_argument('--use-cache', default=False, action='store_true')
    args = parser.parse_args()

    # use all root files by default
    max_files = None
    if args.debug:
        max_files = 1
        if args.use_cache:
            log.info('N(files) limit is irrelevant with the cache')

    log.info('loading samples ..')
    from bbtautau.database import dihiggs_01, dihiggs_10
    dihiggs_01.process(verbose=True, max_files=max_files, use_cache=args.use_cache)
    dihiggs_10.process(verbose=True, max_files=max_files, use_cache=args.use_cache)
    log.info('..done')
    
    log.info('loading regressor weights')
    scikit = joblib.load(os.path.join('cache', args.scikit))
    keras = load_model(os.path.join('cache', args.keras))

    log.info('plotting')
    from bbtautau.utils import features_table, true_mhh
    features_test_HH_01 = features_table(dihiggs_01.fold_1_array)
    features_test_HH_10 = features_table(dihiggs_10.fold_1_array)

    scikit_HH_01 = scikit.predict(features_test_HH_01)
    keras_HH_01 = keras.predict(features_test_HH_01)
    keras_HH_01 = np.reshape(
            keras_HH_01, (keras_HH_01.shape[0], ))
    test_target_HH_01 = ak.flatten(true_mhh(dihiggs_01.fold_1_array))

    scikit_HH_10 = scikit.predict(features_test_HH_10)
    keras_HH_10 = keras.predict(features_test_HH_10)
    keras_HH_10 = np.reshape(
            keras_HH_10, (keras_HH_10.shape[0], ))
    test_target_HH_10 = ak.flatten(true_mhh(dihiggs_10.fold_1_array))

    
    from bbtautau.plotting import compare_ml
    if args.include_mmc:
        from bbtautau.mmc import mmc
        mmc_01, mhh_mmc_01 = mmc(dihiggs_01.fold_1_array)
        mmc_10, mhh_mmc_10 = mmc(dihiggs_10.fold_1_array)
    # 
    compare_ml(
        scikit_HH_10,
        keras_HH_10,
        test_target_HH_10,
        dihiggs_10,
        mmc=mhh_mmc_10 if args.include_mmc else None)

    compare_ml(
        scikit_HH_01,
        keras_HH_01,
        test_target_HH_01,
        dihiggs_01,
        mmc=mhh_mmc_01 if args.include_mmc else None)


