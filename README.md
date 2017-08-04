The PDF statements generated by MIT's new billing system, MITPAY (outsourced to the 3rd party organization TouchNet), cannot be opened in FOSS PDF readers, because they use XFA, a proprietary and deprecated Adobe technology.

`mitpay.py` is a simple Python script that parses these PDFs and outputs something resembling the actual statement. Its output looks something like this:

![screenshot](http://web.mit.edu/~aleksejs/www/screenshots/mitpay_script.png)

(by default, it will actually output real values instead of "[redacted]", but if you need to make a screenshot or something, you can set `REDACTED_MODE` to `True` in the source code)

The script requires Python 3 and the package `pdfrw` (which you can install by running `pip install pdfrw`). On Athena, you can also use the script by running `athrun aleksejs mitpay ./path/to/statement.pdf`.

The script is available under the MIT license (see the file `LICENSE` in this repository). You can use the script for whatever, but remember that there is no warranty. By using the script, you agree that nobody except you cannot be held responsible if the script outputs an incorrect statement, leaks the contents of your statement through electromagnetic radiation, or causes you depression by reminding you how high the tuition is.
