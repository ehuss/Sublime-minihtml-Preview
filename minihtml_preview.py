import sublime
import sublime_plugin
import webbrowser

template = """\
<body id="minihtml-preview">
  <style>
  </style>
  <h1>minihtml Example</h1>
  <p>Enter your own minihtml content on the left to see a preview of it on the
  right.</p>
  <p><a href="https://www.sublimetext.com/docs/3/minihtml.html">minihtml reference</a>
  </p>
</body>
"""


class MinihtmlPreviewCommand(sublime_plugin.ApplicationCommand):

    def run(self):

        sublime.run_command('new_window')
        new_window = sublime.active_window()
        new_window.run_command('set_layout', {
            'cols': [0.0, 0.5, 1.0],
            'rows': [0.0, 1.0],
            'cells': [[0, 0, 1, 1], [1, 0, 2, 1]]
        })
        new_window.focus_group(0)
        edit_view = new_window.new_file()
        edit_view_settings = edit_view.settings()
        edit_view_settings.set('minihtml_preview_edit_view', True)
        edit_view.set_scratch(True)
        edit_view.set_syntax_file('Packages/HTML/HTML.sublime-syntax')
        # Unfortunately Sublime indents on 'insert'
        edit_view.settings().set('auto_indent', False)
        edit_view.run_command('insert', {'characters': template})
        edit_view.settings().set('auto_indent', True)
        new_window.focus_group(1)
        output_view = new_window.new_file()
        output_view.set_scratch(True)
        edit_view_settings.set('minihtml_preview_output_view_id',
                               output_view.id())
        new_window.focus_group(0)


def _on_navigate(href):
    print('Navigate to: %s' % (href,))
    webbrowser.open(href)


class MinihtmlPreviewListener(sublime_plugin.ViewEventListener):

    def __init__(self, view):
        super(MinihtmlPreviewListener, self).__init__(view)
        self.phantom_sets = {}

    @classmethod
    def is_applicable(cls, settings):
        return settings.get('minihtml_preview_edit_view', False)

    def on_modified_async(self):
        output_id = self.view.settings().get('minihtml_preview_output_view_id')
        output_view = next(view for view in self.view.window().views()
            if view.id() == output_id)
        content = self.view.substr(sublime.Region(0, self.view.size()))

        buffer_id = output_view.buffer_id()
        if buffer_id in self.phantom_sets:
            ps = self.phantom_sets[buffer_id]
        else:
            ps = sublime.PhantomSet(output_view, 'minihtml_preview_phantom')
            self.phantom_sets[buffer_id] = ps

        p = sublime.Phantom(sublime.Region(0), content,
                            sublime.LAYOUT_BLOCK, _on_navigate)
        ps.update([p])
