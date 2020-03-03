#!/bin/bash

if [[ ${RUN_SYNC_APP} = true ]] ; then
   python -m src.app
else
   python -m src.async_app
fi