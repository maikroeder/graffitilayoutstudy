module.exports = function (grunt) {
  var package_json = grunt.file.readJSON('package.json');

  //noinspection JSUnresolvedVariable
  var theme_package = package_json.interaktiv_setup.theme_package;

  //noinspection JSUnresolvedVariable
  var packages = package_json.interaktiv_setup.packages;

  // paths to be used inside js linkings
  // css|js locations auto created based on theme
  var paths = {
    node: './node_modules/'
  };

  // Libraries
  //noinspection JSUnresolvedVariable
  var libsJSFiles = package_json.interaktiv_setup.javascript_lib_files;

  // plone resources and js-require problem
  libsJSFiles.unshift('pre.js');
  libsJSFiles.push('post.js');

  // Direct js files which are not defined in a package in the "packages"
  //noinspection JSUnresolvedVariable
  var directJSFiles = package_json.interaktiv_setup.javascript_direct_files;


  //############################## NOT EDIT HERE ##############################

  paths['theme'] = 'src/' + theme_package + '/src/' + theme_package.replace('.', '/') + '/static/';
  paths['var'] = 'var/static/';
  paths['css'] = '<%= paths.var %>css/';
  paths['js'] = '<%= paths.var %>js/';


  // Get all .js files from given packages in "packages"
  // and map them with the sequence.
  var scriptJSFiles = [];
  var suffix_folder = '';
  for (var key in packages) {
    if (!packages.hasOwnProperty(key)) continue;
    suffix_folder = '';
    // Check interaktiv tiles
    if (packages[key].indexOf('interaktiv') !== -1 &&
        packages[key].indexOf('tile') !== -1) {
      suffix_folder = '';
    }
    scriptJSFiles.push(
      'src/' + suffix_folder +
      packages[key] + '/src/' +
      packages[key].replace('.', '/') +
      '/static/**/*.js'
    );
  }

  // plone resources and js-require problem
  scriptJSFiles.unshift('pre.js');
  scriptJSFiles.push('post.js');
  scriptJSFiles = scriptJSFiles.concat(directJSFiles);

  // add theming js files manual and ignore compiled version
  scriptJSFiles.push('<%= paths.js %>**/*.js');
  scriptJSFiles.push('!<%= paths.js %>libs.js');
  scriptJSFiles.push('!<%= paths.js %>script.js');

  // generate all main less files
  var lessFiles = [];

  // add theming less files manual
  lessFiles.push(paths['theme']+'less/*.less');

  for (var key2 in packages) {
    if (!packages.hasOwnProperty(key2)) continue;
    suffix_folder = '';
    // Check interaktiv tiles
    if (packages[key2].indexOf('interaktiv') !== -1 &&
        packages[key2].indexOf('tile') !== -1) {
      suffix_folder = '';
    }
    lessFiles.push(
      'src/' + suffix_folder +
      packages[key2] + '/src/' +
      packages[key2].replace('.', '/') +
      '/static/less/*.less'
    );
  }

  /** @var {function(Object)} grunt.initConfig */
  grunt.initConfig({
    pkg           : grunt.file.readJSON('package.json'),
    paths         : paths,
    "file-creator": {
      createMainLess: {
        "main.less": function (fs, fd, done) {
          var files = grunt.file.expand(lessFiles);
          files.forEach(function (file) {
            var filename = file.split('/').slice(-1)[0];
            if(filename[0] === '_') return;
            //noinspection JSUnresolvedFunction
            fs.writeSync(fd, '@import "' + file + '";\n');
          });
          done();
        }
      }
    },
    less          : {
      theme: {
        options: {
          sourceMap          : true,
          sourceMapFileInline: true,
          compress           : true,
          combineSourceFiles : true
        },
        files  : {
          "<%= paths.css %>style.css": "main.less"
        }
      }
    },
    uglify        : {
      options: {
        banner          : '/*! <%= pkg.name %> <%= grunt.template.today("dd-mm-yyyy HH:MM:ss") %> */\n',
        beautify        : false,
        sourceMap       : true,
        compress        : {},
        mangle          : {
          except: ['jQuery']
        },
        preserveComments: false
      },
      js     : {
        files: {
          '<%= paths.js %>libs.js'  : libsJSFiles,
          '<%= paths.js %>script.js': scriptJSFiles
        }
      }
    },
    clean         : {
      mainLess: ['main.less']
    },
    notify        : {
      watch   : {options: {title: 'Grunt:', message: 'Watch run complete!'}},
      gruntRun: {options: {title: 'Grunt:', message: 'Grunt run complete!'}}
    },
    watch         : {
      less      : {
        files  : lessFiles,
        tasks  : ['file-creator:createMainLess', 'less:theme', 'clean:mainLess', 'notify:watch'],
        options: {
          spawn: false
        }
      },
      javascript: {
        files  : scriptJSFiles,
        tasks  : ['uglify', 'notify:watch'],
        options: {
          spawn: false
        }
      }
    }
  });

  grunt.loadNpmTasks('grunt-contrib-uglify');
  grunt.loadNpmTasks('grunt-contrib-less');
  grunt.loadNpmTasks('grunt-contrib-watch');
  grunt.loadNpmTasks('grunt-notify');
  grunt.loadNpmTasks('grunt-file-creator');
  grunt.loadNpmTasks('grunt-contrib-clean');

  grunt.registerTask('default', ['file-creator:createMainLess', 'less:theme', 'clean:mainLess', 'uglify:js', 'notify:gruntRun']);
  grunt.registerTask('Watch', ['watch']);

};
