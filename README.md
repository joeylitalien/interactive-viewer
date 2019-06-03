# Interactive Viewer 

Online comparison tool for rendering research.

## Dependencies

* [PyEXR](https://github.com/tvogels/pyexr) (0.3.6)
* [NumPy](http://www.numpy.org/) (1.14.2)
* [Matplotlib](https://matplotlib.org/) (2.2.3)
* [Pillow](https://pillow.readthedocs.io/en/latest/index.html) (5.2.0)
* [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) (4.7.1)

To install the latest version of all packages, run

```python3 -m pip install --user -r tools/requirements.txt```

## Creating a new scene

To add a new scene, simply run 

```python3 tools/create_scene.py --name "Jewelry" --root ./```

This will create a new scene directory with an `index.html` template. Here, the `root` argument represents the top directory where the index of all scenes lies.

## Initializing a scene

To add a render, you first need to specify a reference and a base algorithm (e.g. path tracing), along with the metrics to be computed. For instance, this can be done by calling the following command:

```
python3 tools/analyze.py --ref Reference.exr \
                         --tests PT.exr \
                         --dir scenes/jewelry/ \
                         --metrics mape mrse \
                         --epsilon 1e-2 \
                         --clip 0 1
```

The above computes the mean absolute percentage error and the mean relative square error between the reference and the test image. Below is a table of all arguments; run with `--help` for more info.

| Argument | Description | Requirement |
|:----------|:------------|:--|
| `ref` | Reference image | Required |
| `tests` | Test image(s) | Required |
| `dir` | Scene directory (web) | Required |
| `metrics` | List of metrics to compute on new image | Required |
| `epsilon` | Epsilon when computing metric (avoids divison by zero) | Optional (Default: 1e-2) |
| `clip` | Pixel range for false color images | Optional (Default: [0,1]) |


Behind the curtain, this script creates false color images and saves them as LDR  (PNG) images in the scene directory. A thumbnail is also generated for the index. Most importantly, a `data.js` file is written to disk, which is then used by JS to display all images and metrics in the browser. This file can only be created by `tools/analyze.py`, which is why it has to be ran first before adding new renders.

## Adding a new render
The script `tools/render.py` is used to render a new image and add it to an existing scene:

```
python3 tools/render.py --mitsuba ./mitsuba \
                        --ref scenes/jewelry/Reference.exr \
                        --scene ../mitsuba/scenes/jewelry/scene.xml \
                        --dir scenes/jewelry/ \
                        --name "PSSMLT" \
                        --alg "pssmlt" \
                        --timeout 65 \
                        --frequency 60 \
                        --metrics mape mrse
```

| Argument | Description | Requirement |
|:---------|:------------|:--|
| `mitsuba` | Path to Mitsuba executable | Required |
| `ref` | Reference image | Required |
| `scene` | Mitsuba XML scene file | Required |
| `dir` | Scene directory file (web) | Required |
| `name` | Full name of the algorithm | Required |
| `alg` | Mitsuba keyword for algorithm | Required |
| `metrics` | List of metrics to compute on new image | Required |
| `options` | Mitsuba options (e.g. `-D my_var=value`) | Optional
| `timeout` | Kill program after X seconds | Optional |
| `frequency` | Output intermediate images every X seconds | Optional |
| `epsilon` | Epsilon when computing metric (avoids divison by zero) | Optional (Default: 0.01) |
| `clip` | Pixel range for false color images | Optional (Default: [0,1]) |

Note that the scene file _needs_ to have the following line in order to use different integrators:

```
<integrator type="$integrator"> 
    ...
</integrator>
```

If the render name already exists, the script overwrites its false color images and corresponding metrics. If not, it inserts it into the `data.js` dictionary. It is also possible to add an image that was rendered elsewhere, but the dictionary needs to be updated manually to reflect the changes.