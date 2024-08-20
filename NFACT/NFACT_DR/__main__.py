from NFACT.NFACT_base.utils import colours
from NFACT_DR.dual_regression import Dual_regression


def nfact_dr_main():
    print("Currently not implemented")
    exit(0)
    print(
        f"{col['plum']}Performing dual regression on {len(args['ptxdir'])} subjects{col['reset']}"
    )
    dual_reg = Dual_regression(
        algo=args["algo"],
        normalise=args["normalise"],
        parallel=False,
        list_of_files=args["ptxdir"],
        component=components,
        save_type=img_type,
        seeds=seeds,
        nfact_directory=os.path.join(
            args["outdir"],
            "nfact",
        ),
    )
    dual_reg.run()
    return None
