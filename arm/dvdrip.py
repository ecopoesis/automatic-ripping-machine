#!/usr/bin/python3

import sys
import os
import logging
import subprocess
import time
import shlex

from config import cfg


def dvdrip(logfile, disc):
    """
    Rip DVDs with dvdbackup and mkisofs\n
    logfile = Location of logfile to redirect MakeMKV logs to\n
    disc = disc object\n

    Returns path to ripped files.
    """

    logging.info("Starting DVD rip")

    # get filesystem in order
    rawpath = os.path.join(cfg['RAWPATH'], disc.videotitle)
    logging.info("Raw path is " + rawpath)
    moviepath = os.path.join(cfg['MEDIA_DIR'], disc.videotitle)

    if not os.path.exists(rawpath):
        try:
            os.makedirs(rawpath)
        except OSError:
            err = "Couldn't create the raw path: " + rawpath + " Probably a permissions error"
    else:
        logging.info(rawpath + " exists.  Adding timestamp.")
        ts = round(time.time() * 100)
        rawpath = os.path.join(cfg['RAWPATH'], disc.videotitle + "_" + str(ts))
        logging.info("rawpath is " + rawpath)
        try:
            os.makedirs(rawpath)
        except OSError:
            err = "Couldn't create the raw path: " + rawpath + " Probably a permissions error"
            sys.exit(err)

    if not os.path.exists(moviepath):
        try:
            os.makedirs(moviepath)
        except OSError:
            err = "Couldn't create the movie path: " + rawpath + " Probably a permissions error"
    else:
        logging.info(moviepath + " exists.  Adding timestamp.")
        ts = round(time.time() * 100)
        rawpath = os.path.join(cfg['RAWPATH'], disc.videotitle + "_" + str(ts))
        logging.info("rawpath is " + moviepath)
        try:
            os.makedirs(rawpath)
        except OSError:
            err = "Couldn't create the movie path: " + moviepath + " Probably a permissions error"
            sys.exit(err)


    logging.debug("Ripping with dvdbackup...")
    cmd = 'dvdbackup -i {0} -o "{1}" -M -n "{2}"'.format(
                disc.devpath,
                rawpath,
                disc.videotitle
    )

    try:
        dvdbackup = subprocess.run(
            cmd,
            shell=True
        ).decode("utf-8")
        logging.debug("The exit code for dvdbackup is: " + str(dvdbackup.returncode))
    except subprocess.CalledProcessError as mdisc_error:
        err = "Call to dvdbackup failed with code: " + str(dvdbackup.returncode) + "(" + str(dvdbackup.output) + ")"
        logging.error(err)
        return

    isocmd = 'mkisofs -dvd-video -udf -o "{0}"/"{1} - DVDRip 480p.iso" "{2}"/"{3}"'.format(
                moviepath,
                disc.videotitle,
                rawpath,
                disc.videotitle
    )

    try:
        iso = subprocess.run(
            isocmd,
            shell=True
        )
        logging.debug("The exit code for mkisofs is: " + str(iso.returncode))
    except subprocess.CalledProcessError as mdisc_error:
        err = "Call to mkisofs failed with code: " + str(iso.returncode) + "(" + str(iso.output) + ")"
        logging.error(err)
        # print("Error: " + mkv)
        return None

    if cfg['DELRAWFILES']:
        logging.info("Removing raw files")
        shutil.rmtree(rawpath)

    disc.eject()

    logging.info("Exiting DVD Rip processing with return value of: " + moviepath)
    return(moviepath)
