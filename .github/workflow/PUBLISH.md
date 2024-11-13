# PUBLISH (Maintainers only)

## Steps to Publish a New Version to PyPI

1. **Update the Version** in `pyproject.toml`:
   - Manually update the version number in `pyproject.toml` to reflect the new release (e.g., `version = "1.0.0"`).

2. **Commit the Version Update**:
   ```bash
   git add pyproject.toml
   git commit -m "Bump version to 1.0.0"
   ```

3. **Tag the New Version**:
   - Create a tag for the version you want to publish:
   ```bash
   git tag v1.0.0
   ```

4. **Push the Tag to GitHub**:
   - Pushing the tag will trigger the GitHub Actions workflow to automatically build and publish the package to PyPI.
   ```bash
   git push origin v1.0.0
   ```

That’s it! The workflow will handle the build and publish steps, using the configurations in `pyproject.toml`.

