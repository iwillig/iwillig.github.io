# Default recipe - show available commands
default:
    @just --list

# Directory paths
src_dir := "src"
templates_dir := "templates/resume"
output_dir := "assets/static"

# Build the resume HTML from YAML using pandoc
resume:
    pandoc --template {{templates_dir}}/resume.html \
           -f markdown \
           {{src_dir}}/resume.yml \
           -t html \
           -o {{output_dir}}/resume.html
    @echo "Resume built: {{output_dir}}/resume.html"

# Build the resume as PDF (requires wkhtmltopdf or weasyprint)
resume-pdf: resume
    weasyprint {{output_dir}}/resume.html {{output_dir}}/resume.pdf
    @echo "Resume PDF built: {{output_dir}}/resume.pdf"

# Run lektor server for development
serve:
    lektor serve

# Build the site with lektor
build:
    lektor build
    @echo "Site built successfully"

# Build everything (resume + site)
build-all: resume build

# Clean generated files
clean:
    rm -f {{output_dir}}/resume.html
    rm -f {{output_dir}}/resume.pdf
    lektor clean --yes

# Deploy to GitHub Pages
deploy: resume
    lektor deploy ghpages

# Watch resume source and rebuild on changes (requires entr)
watch-resume:
    echo "{{src_dir}}/resume.yml" | entr just resume

# Validate resume HTML with tidy
check: resume
    tidy -q -e {{output_dir}}/resume.html || true
