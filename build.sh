# Cleanup
rm build/ -rf
rm dist/ -rf
rm venv/ -rf

# Build the new version
python setup.py sdist bdist_wheel

# Upload the new version
twine upload --repository pypi dist/*
