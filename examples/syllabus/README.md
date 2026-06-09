# Course Syllabus

A machine learning course syllabus demonstrating the syllabus doctype with grading, schedule, and policy sections.

## Usage

    latexmk -lualatex main.tex

Or using the build system:

    python build.py build-example syllabus

## Class Options

| Option | Value | Description |
|--------|-------|-------------|
| doctype | syllabus | Course syllabus doctype |
| language | english | English language support |
| institution | none | No institutional branding |

## Features Demonstrated

- `objectives` environment for learning objectives
- `gradingpolicy` environment with `\gradingitem{component}{weight}`
- `scheduleentry{week}{dates}{topic}` for course schedule
- Subsections for attendance, late work, academic integrity, accommodations
- `booktabs` table for weekly schedule
- Mathematical notation in learning objectives

## Notes

The syllabus doctype provides specialized environments for course metadata. Grading weights should sum to 100. The schedule table supports up to 12 weeks with exam date overrides.
