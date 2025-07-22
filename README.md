# REALAssociator
## Related Publication

[![DOI](https://img.shields.io/badge/DOI-10.1126%2Fscience.adt6389-blue)](https://doi.org/10.1126/science.adt6389)

If you use this code or data, please cite the following paper: <br>
Rintaroh Suzuki _et al._, The forearc seismic belt: A fluid pathway constraining down-dip megathrust earthquake rupture. _Science_ **389**, 190-194 (2025). https://doi.org/10.1126/science.adt6389

## Summary

![](docs/assets/REALAssociator_overview.png)
 
* Tool to associate phase data from PhaseNet (Zhu and Beroza, 2019) using REAL (Zhang et al., 2019).
* Easy to run on various OS by using **docker**.

## Requirements
* OS <br>
  Support Windows, macOS and Linux

* (Only required for Windows) Git Bash <br>
  https://gitforwindows.org/ <br>
  For Windows, run "Git Bash" and use it to execute commands for following steps.

* docker <br>
  * Installation <br>
  For Windows and macOS, install "Docker Desktop" and run it to activate docker. <br>
  https://docs.docker.com/get-docker/ <br>
  For Linux, install "Docker Engine". <br>
  https://docs.docker.com/engine/install/ <br>

  * (Only required for Linux) Create the docker group and add your user <br>
  https://docs.docker.com/engine/install/linux-postinstall/#manage-docker-as-a-non-root-user <br>

  * Verify installation <br>
    ```
    $ docker run hello-world
    ...
    Hello from Docker!
    This message shows that your installation appears to be working correctly.
    ...
    ```
    
## Usage
* Installation
  ```
  $ git clone https://github.com/rintr-suzuki/REALAssociator.git
  $ cd REALAssociator
  ```

* Execution
  ```
  $ ./REALAssociator.bash --infile data/picks.json
  # See 'data' directory for the result.
  ```

* See [here](docs/README-usage.md) for the detailed information.

* See [here](docs/Tips.md) for the tips of this tool.

## Acknowledgements
* This program is forked from the original version to test. Original version is [here](https://github.com/Dal-mzhang/REAL). <br>
See LISENCE for the copyright notice.

## References
* Hasegawa, A., Umino, N., & Takagi, A. (1978), Double-planed structure of the deep seismic zone in the northeastern Japan arc. Tectonophysics, 47(1–2), 43–58. https://doi.org/10.1016/0040-1951(78)90150-6
* Zhang, M., W.L. Ellsworth, & Beroza, G. C. (2019), Rapid Earthquake Association and Location, Seismol. Res. Lett., 90.6, 2276-2284. https://doi.org/10.1785/0220190052
