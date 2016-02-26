'use strict';

var gulp = require('gulp');
var sass = require('gulp-sass');
var concat = require('gulp-concat');
var uglify = require('gulp-uglify');

gulp.task('sass', function () {
  gulp.src([
      './scss/bootstrap.scss',
      './bower_components/bootstrap-datepicker/dist/css/bootstrap-datepicker.css',
      './bower_components/font-awesome/css/font-awesome.css',
      './bower_components/c3/c3.css',
      './bower_components/select2/dist/css/select2.css',
      './scss/bootstrap_overrides.scss',
      './scss/utils.scss',
      './scss/components.scss'
    ])
    .pipe(sass({outputStyle: 'compressed'}))
    .pipe(concat('all.css'))
    .pipe(gulp.dest('../static/common/css'));
});

gulp.task('sass:watch', ['sass'], function () {
  gulp.watch('./scss/**/*.scss', ['sass']);
});

gulp.task('js', function () {
  gulp.src([
      './bower_components/jquery/dist/jquery.js',
      './bower_components/bootstrap-sass/assets/javascripts/bootstrap.js',
      './bower_components/jquery-maskmoney/dist/jquery.maskMoney.js',
      './bower_components/d3/d3.js',
      './bower_components/c3/c3.js',
      './bower_components/jquery.floatThead/dist/jquery.floatThead.js',
      './bower_components/bootstrap-datepicker/dist/js/bootstrap-datepicker.js',
      './bower_components/bootstrap-datepicker/dist/locales/bootstrap-datepicker.pt-BR.min.js',
      './bower_components/select2/dist/js/select2.js',
      './bower_components/select2/dist/js/i18n/pt-BR.js',
      './bower_components/select2/dist/js/i18n/en.js',
      './js/d3_config.js',
      './js/app.js'
    ])
    .pipe(concat('all.js'))
    .pipe(uglify())
    .pipe(gulp.dest('../static/common/js'));
});

gulp.task('js:watch', ['js'], function () {
  gulp.watch('./js/**/*.js', ['js']);
});

gulp.task('default', ['sass', 'js']);
