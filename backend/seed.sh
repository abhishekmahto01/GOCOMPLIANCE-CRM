#!/bin/sh
set -e

echo "==> [1/5] Seeding modules..."
python -m app.scripts.seed_modules

echo "==> [2/5] Seeding departments..."
python -m app.scripts.seed_departments

echo "==> [3/5] Seeding designations..."
python -m app.scripts.seed_designations

echo "==> [4/5] Seeding companies..."
python -m app.scripts.seed_companies

echo "==> [5/5] Seeding services..."
python -m app.scripts.seed_services

echo "==> [✔] All base system data seeded successfully!"
