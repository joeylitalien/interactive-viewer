python3 render.py --mitsuba /home/joey/Documents/mitsuba/cmake-build-release/binaries/mitsuba \
                  --ref ../../mitsuba/scenes/jewelry/Reference.exr \
                  --scene ../../mitsuba/scenes/jewelry/scene_grid.xml \
                  --dir ../scenes/jewelry/ \
                  --name "PSSMLT" \
                  --alg "pssmlt" \
                  --timeout 10 \
                  --frequency 8 \
                  --metrics mape smape mrse
