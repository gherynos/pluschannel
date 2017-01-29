/*
 Copyright (C) 2012-2017  Luca Zanconato (<luca.zanconato@nharyes.net>)

 This file is part of Plus Channel.

 Plus Channel is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 Plus Channel is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with Plus Channel.  If not, see <http://www.gnu.org/licenses/>.
 */

module.exports = function (grunt) {

    var path = require('path');

    // Project configuration
    grunt.initConfig({

        pkg: grunt.file.readJSON('package.json'),

        uglify: {

            options: {

                banner: '/*! <%= pkg.name %> <%= grunt.template.today("yyyy-mm-dd") %> */\n'
            },
            build: {

                src: './app/static/js/app.js',
                dest: './app/static/js/app.js'
            }
        },

        concat: {

            options: {},
            dist: {
                src: [

                    './temp/min-safe-app.js',
                    './temp/min-safe-app-shared.js',
                    './temp/min-safe-app-components.js'
                ],
                dest: './app/static/js/app.js'
            }
        },

        ngAnnotate: {
            options: {

                singleQuotes: true
            },
            app: {

                files: {

                    './temp/min-safe-app.js': ['./angular-app/app.module.js', './angular-app/app.routes.js'],
                    './temp/min-safe-app-shared.js': ['./angular-app/shared/**/*.js'],
                    './temp/min-safe-app-components.js': ['./angular-app/components/**/*.js']
                }
            }
        },

        shell: {

            pythonServer: {

                options: {

                    stdout: true
                },
                command: '. venv/bin/activate && python run.py && deactivate'
            }
        },

        copy: {

            templates: {

                files: [{

                    expand: true,
                    flatten: true,
                    src: ['./angular-app/**/*.tpl.html'],
                    dest: './app/static/tpl'
                }]
            },

            deploy: {

                files: [{

                    expand: true,
                    src: ['./app/**', './app.wsgi', './config.py', './config.yaml', './requirements.txt', './db.sqlite', './credentials.json'],
                    dest: './deploy'
                }]
            }
        },

        clean: {

            deploy: './deploy',
            initial: ['./deploy', './temp', './app/static/js/app.js', './app/static/tpl/*.tpl.html']
        },

        bower: {

            install: {

                options: {

                    targetDir: './app/static',
                    install: false,
                    verbose: false,
                    prune: true,
                    cleanTargetDir: false,
                    cleanBowerDir: false,
                    layout: function (type, component, source) {
                        return path.join(type);
                    }
                }
            }
        }
    });

    // load grunt tasks
    grunt.loadNpmTasks('grunt-contrib-concat');
    grunt.loadNpmTasks('grunt-contrib-uglify');
    grunt.loadNpmTasks('grunt-ng-annotate');
    grunt.loadNpmTasks('grunt-shell');
    grunt.loadNpmTasks('grunt-newer');
    grunt.loadNpmTasks('grunt-contrib-copy');
    grunt.loadNpmTasks('grunt-contrib-clean');
    grunt.loadNpmTasks('grunt-bower-task');

    // tasks
    grunt.registerTask('copy-templates', ['newer:copy:templates']);
    grunt.registerTask('generate-app', ['copy-templates', 'newer:ngAnnotate', 'newer:concat']);
    grunt.registerTask('generate-ugly-app', ['generate-app', 'newer:uglify']);
    grunt.registerTask('dev-server', ['generate-app', 'shell:pythonServer']);
    grunt.registerTask('clear', ['clean:initial']);
    grunt.registerTask('default', ['clear', 'generate-ugly-app', 'clean:deploy', 'copy:deploy']);
};
