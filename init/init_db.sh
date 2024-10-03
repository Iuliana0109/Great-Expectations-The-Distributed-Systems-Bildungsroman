#!/bin/bash
set -e

# Create the CompetitionService database
psql -U user -d postgres -c "CREATE DATABASE CompetitionService;"
