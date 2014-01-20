c = get_config()


## TerminalIPythonApp configuration

# Whether to display a banner upon starting IPython.
c.TerminalIPythonApp.display_banner = False


## TerminalInteractiveShell configuration

# 
c.TerminalInteractiveShell.separate_in = ''


## PromptManager configuration
# This is the primary interface for producing IPython's prompts.

# Output prompt. '\#' will be transformed to the prompt number
c.PromptManager.out_template = '[\\#] '

# Continuation prompt.
c.PromptManager.in2_template = '.\\D. '

# Input prompt.  '\#' will be transformed to the prompt number
c.PromptManager.in_template = '[\\#] '

