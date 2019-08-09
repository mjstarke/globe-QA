# globe-QA
Quality assurance and plotting tools for GLOBE Observer data.
Learn more about GLOBE Observer at [the official website](https://observer.globe.gov).

**This readme is a work in progress!**

Check the `example_*.py` files for some basic, thoroughly-commented procedures, and
the `figure_*.py` files for some more involved data analysis.  Note that some
figures require external data outside of GLOBE to function - see `figure_common.py`
for details.

## Getting data
GLOBE Observer data is freely available can be obtained in JSON format from the [GLOBE API](https://www.globe.gov/globe-data/globe-api).
However, for simple queries, you can use `tools.download_from_api()`.  This function
will give downloaded files a standard name (which can be adjusted with the `download_dest` kwarg)
and, by default, if a file by that name already exists, the download will not be
attempted - instead, the local file is used.

## tqdm usage
[tqdm](https://github.com/tqdm/tqdm) is used to print progress bars from many of the functions in `tools.py`.
By default, it is enabled.  If you would like to turn it off for a given function, you can pass
`tqdm=figure_common.quiet` as a kwarg.
You can also pass `tqdm=figure_common.simple`, which will print only the description.

## Quality checker
The `Observation` class has a method `check_for_flags()` that can be used to quality
check itself.  This method can be called on a list by using
`tools.do_quality_check()`.  Each `Observation` will then gain a `flags` attribute
that contains a list of all flags raised.  Each flag is represented by a
two-letter code whose meaning is defined in `Observation._flag_definitions`.

### Adding a flag

Adding a flag requires three things:
1. A method that checks the `Observation` and raises a flag whenever certain
criteria are met
1. A call to that method in `Observation._check_for_flags()`
1. A definition for the flag in `Observation._flag_definitions`