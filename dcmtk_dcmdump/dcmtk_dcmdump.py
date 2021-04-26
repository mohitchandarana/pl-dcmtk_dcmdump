#
# dcmtk_dcmdump ds ChRIS plugin app
#
# (c) 2021 Fetal-Neonatal Neuroimaging & Developmental Science Center
#                   Boston Children's Hospital
#
#              http://childrenshospital.org/FNNDSC/
#                        dev@babyMRI.org
#

import os

from chrisapp.base import ChrisApp
import      pudb
import      subprocess
import      pfmisc


Gstr_title = """


     _                _   _         _                    _                       
    | |              | | | |       | |                  | |                      
  __| | ___ _ __ ___ | |_| | __  __| | ___ _ __ ___   __| |_   _ _ __ ___  _ __  
 / _` |/ __| '_ ` _ \| __| |/ / / _` |/ __| '_ ` _ \ / _` | | | | '_ ` _ \| '_ \ 
| (_| | (__| | | | | | |_|   < | (_| | (__| | | | | | (_| | |_| | | | | | | |_) |
 \__,_|\___|_| |_| |_|\__|_|\_\ \__,_|\___|_| |_| |_|\__,_|\__,_|_| |_| |_| .__/ 
                            ______                                        | |    
                           |______|                                       |_|    


"""

Gstr_synopsis = """

    NAME

       dcmtk_dcmdump.py 

    SYNOPSIS

        python dcmtk_dcmdump.py                                         \\
            [-h] [--help]                                               \\
            [--json]                                                    \\
            [--man]                                                     \\
            [--meta]                                                    \\
            [--savejson <DIR>]                                          \\
            [-v <level>] [--verbose <level>]                            \\
            [--version]                                                 \\
            [-i <DICOM file>] [--inputFile <DICOM file>]                \\
            [--noJobLogging]                                            \\
            [-o <TXT file>.txt] [--outputFileStem <TXT file>.txt]       \\
            <inputDir>                                                  \\
            <outputDir> 

    BRIEF EXAMPLE

        * Bare bones execution

            docker run --rm -u $(id -u)                             \
                -v $(pwd)/in:/incoming -v $(pwd)/out:/outgoing      \
                mchandarana/pl-dcmtk_dcmdump:1.0.0 dcmtk_dcmdump -i <DICOM file>                       \
                /incoming /outgoing

    DESCRIPTION

        `dcmtk_dcmdump.py` ...

    ARGS

        [-h] [--help]
        If specified, show help message and exit.
        
        [--json]
        If specified, show json representation of app and exit.
        
        [--man]
        If specified, print (this) man page and exit.

        [--meta]
        If specified, print plugin meta data and exit.
        
        [--savejson <DIR>] 
        If specified, save json representation file to DIR and exit. 
        
        [-v <level>] [--verbose <level>]
        Verbosity level for app.
        
        [--version]
        If specified, print version number and exit.

        [--noJobLogging]
        Turn off per-job logging to file system

        [-i <DICOM file>] [--inputFile <DICOM file>]
        Name of the input file within the inputDir

        [-o <TXT file>.txt] [--outputFileStem <TXT file>.txt]
        output file stem name (with extension)
"""


class Dcmtk_dcmdump(ChrisApp):
    """
    An app to ...
    """
    PACKAGE                 = __package__
    TITLE                   = 'A ChRIS plugin app that uses the dcmdump utility from dcext file'
    CATEGORY                = ''
    TYPE                    = 'ds'
    ICON                    = ''   # url of an icon image
    MIN_NUMBER_OF_WORKERS   = 1    # Override with the minimum number of workers as int
    MAX_NUMBER_OF_WORKERS   = 1    # Override with the maximum number of workers as int
    MIN_CPU_LIMIT           = 1000 # Override with millicore value as int (1000 millicores == 1 CPU core)
    MIN_MEMORY_LIMIT        = 200  # Override with memory MegaByte (MB) limit as int
    MIN_GPU_LIMIT           = 0    # Override with the minimum number of GPUs as int
    MAX_GPU_LIMIT           = 0    # Override with the maximum number of GPUs as int

    # Use this dictionary structure to provide key-value output descriptive information
    # that may be useful for the next downstream plugin. For example:
    #
    # {
    #   "finalOutputFile":  "final/file.out",
    #   "viewer":           "genericTextViewer",
    # }
    #
    # The above dictionary is saved when plugin is called with a ``--saveoutputmeta``
    # flag. Note also that all file paths are relative to the system specified
    # output directory.
    OUTPUT_META_DICT = {}

    def define_parameters(self):
        """
        Define the CLI arguments accepted by this plugin app.
        Use self.add_argument to specify a new app argument.
        """
        self.add_argument("--noJobLogging",
                            help        = "Turn off per-job logging to file system",
                            type        = bool,
                            dest        = 'noJobLogging',
                            action      = 'store_true',
                            optional    = True,
                            default     = True)

        self.add_argument("--verbose",
                            type        = str,
                            optional    = True,
                            help        = "verbosity level for app",
                            dest        = 'verbose',
                            default     = "1")

        self.add_argument('-i', '--inputFile',
                            dest        = 'inputFile',
                            type        = str,
                            optional    = True,
                            help        = 'name of the input file within the inputDir',
                            default     = ''
                        )

        self.add_argument('-o', '--outputFileStem',
                            dest        = 'outputFileStem',
                            type        = str,
                            optional    = True,
                            help        = 'output file stem name (with optional extension)',
                            default     = 'results.txt'
                        )
    
    def job_run(self, str_cmd):
        """
        Running some CLI process via python is cumbersome. The typical/easy
        path of
                            os.system(str_cmd)
        is deprecated and prone to hidden complexity. The preferred
        method is via subprocess, which has a cumbersome processing
        syntax. Still, this method runs the `str_cmd` and returns the
        stderr and stdout strings as well as a returncode.
        Providing readtime output of both stdout and stderr seems
        problematic. The approach here is to provide realtime
        output on stdout and only provide stderr on process completion.
        """
        d_ret       : dict = {
            'stdout':       "",
            'stderr':       "",
            'cmd':          "",
            'cwd':          "",
            'returncode':   0
        }
        str_stdoutLine  : str   = ""
        str_stdout      : str   = ""

        p = subprocess.Popen(
                    str_cmd.split(),
                    stdout      = subprocess.PIPE,
                    stderr      = subprocess.PIPE,
        )

        # Realtime output on stdout
        str_stdoutLine  = ""
        str_stdout      = ""
        while True:
            stdout      = p.stdout.readline()
            if p.poll() is not None:
                break
            if stdout:
                str_stdoutLine = stdout.decode()
                if int(self.args['verbosity']):
                    print(str_stdoutLine, end = '')
                str_stdout      += str_stdoutLine
        d_ret['cmd']        = str_cmd
        d_ret['cwd']        = os.getcwd()
        d_ret['stdout']     = str_stdout
        d_ret['stderr']     = p.stderr.read().decode()
        d_ret['returncode'] = p.returncode
        if int(self.args['verbosity']) and len(d_ret['stderr']):
            print('\nstderr its here: \n%s' % d_ret['stderr'])
        return d_ret

    def job_stdwrite(self, d_job, str_outputDir, str_prefix = ""):
        """
        Capture the d_job entries to respective files.
        """
        if not self.args['noJobLogging']:
            for key in d_job.keys():
                with open(
                    '%s/%s%s' % (str_outputDir, str_prefix, key), "w"
                ) as f:
                    f.write(str(d_job[key]))
                    f.close()
        return {
            'status': True
        }

    def run(self, options):
        """
        Define the code to be run by this plugin app.
        """
        
        options.verbosity   = options.verbose
        self.args           = vars(options)
        self.__name__       = "dcmtk_dcmdump"
        self.dp             = pfmisc.debug(
                                 verbosity   = int(self.args['verbosity']),
                                 within      = self.__name__
                             )
        
        print(Gstr_title)
        print('Version: %s' % self.get_version())

        inputfilepath = os.path.join(options.inputdir, options.inputFile)
       
        outputfilepath = os.path.join(options.outputdir, options.outputFileStem)

        # Define command as string and then split() into list format
        str_cmd = 'dcmdump %s' % (inputfilepath)

        print("Running %s..." % str_cmd)

        d_job = self.job_run(str_cmd)
        
        # Copies std_out to text_file
        with open('%s' % (outputfilepath), "w") as f:
            f.write(str(d_job['stdout']))
            f.close()

        self.job_stdwrite(
                d_job, options.outputdir,
                options.inputFile
            )

    def show_man_page(self):
        """
        Print the app's man page.
        """
        print(Gstr_synopsis)
