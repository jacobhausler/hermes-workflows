import sys
_BLOCKED = {'hermes_cli', 'hermes_constants', 'agent', 'hermes_yaml', 'hermes_platform', 'hermes_bootstrap'}
class _Blocker:
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.')[0] in _BLOCKED:
            raise ImportError('%s blocked (nocore test mode)' % fullname)
        return None
sys.meta_path.insert(0, _Blocker())
