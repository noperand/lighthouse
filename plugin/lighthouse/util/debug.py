import sys
import cProfile
import traceback

from .log import lmsg
from .disassembler import disassembler

#------------------------------------------------------------------------------
# Debug
#------------------------------------------------------------------------------
#
#    This file contains random snippets of code that I frequently use while
#    developing and debugging parts of lighthouse. I don't expect any of this
#    code to be active or in use for major releases.
#

#------------------------------------------------------------------------------
# Call Profiling
#------------------------------------------------------------------------------

pr = cProfile.Profile()

def profile(func):
    """
    A simple function profiling decorator.
    """
    def wrap(*args, **kwargs):
        global pr
        pr.enable()
        result = func(*args, **kwargs)
        pr.disable()
        pr.print_stats(sort="tottime")
        return result
    return wrap

#------------------------------------------------------------------------------
# Function Line Profiling
#------------------------------------------------------------------------------

# from: https://gist.github.com/sibelius/3920b3eb5adab482b105
try:
    from line_profiler import LineProfiler
    def line_profile(func):
        def profiled_func(*args, **kwargs):
            try:
                profiler = LineProfiler()
                profiler.add_function(func)
                profiler.enable_by_count()
                return func(*args, **kwargs)
            finally:
                profiler.print_stats()
        return profiled_func

except ImportError:
    def line_profile(func):
        def nothing(*args, **kwargs):
            return func(*args, **kwargs)
        return nothing

#------------------------------------------------------------------------------
# Error Logging
#------------------------------------------------------------------------------

def catch_errors(func):
    """
    A simple catch-all decorator to try and log Lighthouse crashes.

    This will be used to wrap high-risk or new code, in an effort to catch
    and fix bugs without leaving the user in a stuck state.
    """

    def wrap(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()

            st = traceback.format_stack()[:-1]
            ex = traceback.format_exception(exc_type, exc_value, exc_traceback)[2:]

            # log full crashing callstack to console
            full_error = st + ex
            full_error = ''.join(full_error).splitlines()

            lmsg("Lighthouse experienced an error... please file an issue on GitHub with this traceback:")
            lmsg("")
            for line in full_error:
                lmsg(line)

            # notify the user that a bug occurred
            disassembler.warning(
                "Something bad happend to Lighthouse :-(\n\n" \
                "Please file an issue on GitHub with the traceback from your disassembler console."
            )

    return wrap

#------------------------------------------------------------------------------
# Module Line Profiling
#------------------------------------------------------------------------------

if False:
    from line_profiler import LineProfiler
    lpr = LineProfiler()

    # change this to the target file / module to profile
    import lighthouse.metadata as metadata
    lpr.add_module(metadata)

    # put this code somewhere to dump results:
    #global lpr
    #lpr.enable_by_count()
    #lpr.disable_by_count()
    #lpr.print_stats(stripzeros=True)
