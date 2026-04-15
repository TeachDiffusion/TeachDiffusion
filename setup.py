"""TeachDiffusion: Open-Source Video Diffusion for Math Education."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = [
        line.strip()
        for line in f
        if line.strip() and not line.startswith("#")
    ]

setup(
    name="teachdiffusion",
    version="0.1.0",
    author="Calyx",
    author_email="",
    description="Open-source video diffusion model for math education",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/TeachDiffusion/TeachDiffusion",
    project_urls={
        "Bug Tracker": "https://github.com/TeachDiffusion/TeachDiffusion/issues",
        "Documentation": "https://github.com/TeachDiffusion/TeachDiffusion/tree/main/docs",
        "Source Code": "https://github.com/TeachDiffusion/TeachDiffusion",
    },
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.10",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "black>=23.0",
            "isort>=5.0",
            "flake8>=6.0",
        ],
        "video": [
            "torch>=2.0",
            "diffusers>=0.25",
            "accelerate>=0.25",
            "transformers>=4.35",
        ],
        "manim": [
            "manim>=0.18",
        ],
    },
    entry_points={
        "console_scripts": [
            "teachdiffusion=teachdiffusion.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Education",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Multimedia :: Video",
    ],
    keywords="video-diffusion math education teaching ai open-source",
)
