# Basic simulation ns-3 module

[![Build Status](https://travis-ci.org/snkas/basic-sim.svg?branch=master)](https://travis-ci.org/snkas/basic-sim) [![codecov](https://codecov.io/gh/snkas/basic-sim/branch/master/graph/badge.svg)](https://codecov.io/gh/snkas/basic-sim)

This ns-3 module is intended to make experimental simulation of networks a bit easier. It has a wrapper to take care of loading in run folder configurations (e.g., runtime, random seed), a topology abstraction, an additional routing abstraction called "arbiter routing", a heuristic TCP optimizer, and a few handy applications.

**This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details (in ./LICENSE).**


## Installation

1. Install the following dependencies:

   * Python 3.7+
   * MPI:
     ```
     sudo apt-get install mpic++
     sudo apt-get install libopenmpi-dev
     ```
   * lcov: `sudo apt-get install lcov`
   
   Additionally, if you are going to make use of functionality beyond the C++ ns-3 module:
   
   * gnuplot (for plotting): `sudo apt-get install gnuplot`
   * numpy (for plotting): `pip install numpy`
   * statsmodels (for plotting): `pip install statsmodels`
   * exputilpy (for testing and plotting): `pip install git+https://github.com/snkas/exputilpy.git`

## Information
This was previously a submodule, but recent versions are not anymore compatible with hypatia. So code was kept, and submodule removed.
The source can be found here: https://github.com/snkas/basic-sim/tree/3b32597c183e1039be7f0bede17d36d354696776


## Getting started

Documentation (including tutorials) to get started is located in the `doc/` folder.
A good starting point is: `doc/getting_started.md`.


## Testing

To perform the full range of testing of this module (Python 3.7+):

```
sudo apt-get update
sudo apt-get -y install mpic++
sudo apt-get -y install libopenmpi-dev
sudo apt-get -y install lcov
sudo apt-get -y install gnuplot
pip install numpy
pip install statsmodels
pip install git+https://github.com/snkas/exputilpy.git
cd build
bash build.sh
bash test.sh
bash tutorial.sh
bash example.sh
```


## Acknowledgements

Refactored, extended and maintained by Simon.

Contributions were made by (former) students in the NDAL group who did a project or their thesis, among which: Hussain, Hanjing (list will continue to be updated).

The ECMP routing hashing function is inspired by https://github.com/mkheirkhah/ecmp (accessed: February 20th, 2020), though heavily modified.
