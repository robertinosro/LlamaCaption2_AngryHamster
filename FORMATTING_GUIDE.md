# LlamaScribe Caption Formatting Guide

## Overview

LlamaScribe now features a flexible caption formatting system that allows you to customize how AI-generated image descriptions are formatted. This guide explains how to use these features effectively.

## The Formatting Tab

The new "Formatting" tab in LlamaScribe provides complete control over caption formatting:

![Formatting Tab](formatting_tab_screenshot.png)

### Available Options

1. **Caption Prefix**
   - Enable/disable with the checkbox
   - Customize content in the text area
   - Applied before the AI-generated description

2. **Caption Suffix**
   - Enable/disable with the checkbox
   - Customize content in the text area
   - Applied after the AI-generated description

## Default Formatting

LlamaScribe comes with carefully crafted default formatting:

### Default Prefix
```
A photo of a woman, bloobikkx1, curvy blonde with (a well-defined neck:1.3) and (natural proportions:1.2), 
```

### Default Suffix
```
(masterpiece, ultra-realistic, high-definition, 8K, cinematic lighting),(professional photography:1.4), (sharp focus:1.2), (studio lighting:1.2), (clear details:1.3), (professional atmosphere:1.3)
```

## How Caption Formatting Works

When processing images, LlamaScribe:

1. Captures the image with a vision AI model
2. Generates a detailed description with a text AI model
3. Applies your custom formatting (prefix + AI description + suffix)
4. Saves the formatted caption as a text file

## Tips for Effective Formatting

### Prefix Tips
- Use the prefix to establish the subject and basic attributes
- Include any specific character traits or features you want to emphasize
- Use weight modifiers in parentheses (like `(feature:1.2)`) to control emphasis

### Suffix Tips
- Add quality enhancements and style modifiers
- Include technical aspects like lighting and focus
- Group related concepts with parentheses
- Use weight modifiers to fine-tune importance

## Advanced Customization

For permanent changes to the default formatting:

1. Open `LlamaScribe.pyw` in a text editor
2. Locate the `DEFAULT_CAPTION_PREFIX` and `DEFAULT_CAPTION_SUFFIX` constants (around line 25)
3. Modify these values to your preferred defaults
4. Save the file

## Example Custom Formats

### Portrait Photography Format
- **Prefix**: `A professional portrait photograph of a person, `
- **Suffix**: ` (studio lighting:1.3), (professional photography:1.4), (high resolution:1.2)`

### Landscape Photography Format
- **Prefix**: `A breathtaking landscape showing `
- **Suffix**: ` (golden hour:1.3), (dramatic lighting:1.2), (ultra high definition:1.4), (award-winning photography:1.3)`

### Product Photography Format
- **Prefix**: `A detailed product photograph of `
- **Suffix**: ` (product photography:1.4), (studio lighting:1.3), (white background:1.2), (commercial quality:1.3), (advertising photograph:1.2)`

## Troubleshooting

- **Formatting not applied**: Ensure the respective checkboxes are checked
- **Changes not saved**: Remember that changes only apply to the current session
- **Text too long**: Very long prefixes or suffixes might be truncated by some AI image generation systems

## Feedback and Suggestions

If you have ideas for improving the formatting system or want to share your custom formats, please open an issue on our GitHub repository.
