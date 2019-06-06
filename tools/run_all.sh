python3 analyze.py --ref Reference.exr \
                   --tests PSS.exr PSS-Gaussian.exr DRM.exr \
                   --names "PSS Kelemen" "PSS Gaussian \u03C3=0.01" "DR Trunc(50)+Gauss(0.0025)" \
                   --metrics l2 mape mrse \
                   --partials pssmlt_partial/ pssmlt-gaussian_partial drmlt_partial \
                   --dir ../scenes/spaceship/