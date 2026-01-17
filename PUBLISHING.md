# Publishing to PyPI

This guide explains how to publish Quick Tasks to PyPI.

## Prerequisites

1. **PyPI Account**: Create accounts on:
   - [PyPI](https://pypi.org/account/register/) (production)
   - [TestPyPI](https://test.pypi.org/account/register/) (testing)

2. **Install Tools**:
   ```bash
   pip install --upgrade build twine
   ```

3. **API Tokens**: Generate API tokens:
   - Go to Account Settings → API tokens
   - Create a token for uploading packages
   - Save the token securely

## Publishing Steps

### 1. Update Version

Edit `pyproject.toml` and update the version:
```toml
[project]
name = "quick-tasks"
version = "1.0.1"  # Update this
```

### 2. Build the Package

```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info/

# Build source distribution and wheel
python -m build
```

This creates:
- `dist/quick_tasks-X.Y.Z.tar.gz` (source distribution)
- `dist/quick_tasks-X.Y.Z-py3-none-any.whl` (wheel)

### 3. Test on TestPyPI (Recommended)

```bash
# Upload to TestPyPI
python -m twine upload --repository testpypi dist/*

# Test installation
pip install --index-url https://test.pypi.org/simple/ quick-tasks
```

### 4. Publish to PyPI

```bash
# Upload to PyPI
python -m twine upload dist/*
```

You'll be prompted for:
- Username: `__token__`
- Password: Your API token (starts with `pypi-`)

### 5. Verify Installation

```bash
# Install from PyPI
pip install quick-tasks

# Test
quick-tasks --version  # if version command exists
```

## Alternative: Using GitHub Actions

Create `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  pypi-publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install --upgrade pip
          pip install build twine
      
      - name: Build package
        run: python -m build
      
      - name: Publish to PyPI
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
        run: twine upload dist/*
```

Add your PyPI token as a GitHub secret named `PYPI_API_TOKEN`.

## Version Management

Follow [Semantic Versioning](https://semver.org/):
- `MAJOR.MINOR.PATCH`
- `1.0.0` → First stable release
- `1.0.1` → Bug fixes
- `1.1.0` → New features (backwards compatible)
- `2.0.0` → Breaking changes

## Checklist Before Publishing

- [ ] All tests pass
- [ ] Documentation is up to date
- [ ] README.md is accurate
- [ ] Version number is updated
- [ ] CHANGELOG is updated (if exists)
- [ ] Package builds without errors
- [ ] Tested on TestPyPI
- [ ] All dependencies are specified correctly
- [ ] License file is included
- [ ] .gitignore excludes sensitive files

## Troubleshooting

### Error: Package already exists

- You cannot overwrite existing versions on PyPI
- Increment the version number in `pyproject.toml`
- Rebuild and upload again

### Error: Invalid credentials

- Make sure you're using `__token__` as username
- Check that your API token is correct
- Ensure token has upload permissions

### Error: Missing files in distribution

- Check `MANIFEST.in`
- Verify `pyproject.toml` package configuration
- Test by extracting the tar.gz and inspecting contents

## Post-Publishing

1. **Tag the release on GitHub**:
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

2. **Create GitHub Release**: Add release notes

3. **Announce**: Share on relevant platforms

4. **Monitor**: Watch for issues and feedback

## Resources

- [PyPI Documentation](https://packaging.python.org/)
- [Twine Documentation](https://twine.readthedocs.io/)
- [Python Packaging Guide](https://packaging.python.org/tutorials/packaging-projects/)
