import tkinter as tk


class MultilineEntry(tk.Text):
    '''UI element providing multiline user entry'''
    def __init__(self, master, max_lines, *args, **kwargs):
        tk.Text.__init__(self, master, *args, **kwargs)
        self.line_count = 0
        self.MAX_LINES = max_lines
        self._resizing = False

        self.bind('<<Modified>>', self.resize)

    def resize(self, event=None):
        if not self._resizing:
            # Not a configure event, check the modified flag
            modified = self.edit_modified()

            if not modified:
                # Do not need to do anything if text not modified
                return
            else:
                # Clear modified flag
                self.edit_modified(False)

        # Count number of lines needed to display text
        resized_line_count = self.count(1.0, tk.END, 'displaylines')[0]

        if resized_line_count != self.line_count \
           and resized_line_count <= self.MAX_LINES:
            # Height has changed within limits
            self.configure(height=resized_line_count)

        self.line_count = resized_line_count
        self._resizing = False

    def on_configure(self, event):
        # NOTE 'event.width' is the pixel width of the text
        # Only resize every ~200ms
        if not self._resizing:
            self._resizing = True
            self.after(200, self.resize)
