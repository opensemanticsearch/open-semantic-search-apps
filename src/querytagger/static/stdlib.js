// **************************************************************************
// Copyright 2007 - 2009 Tavs Dokkedahl
// Contact: http://www.jslab.dk/contact.php
//
// This file is part of the JSLab Standard Library (JSL) Program.
//
// JSL is free software; you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation; either version 3 of the License, or
// any later version.
//
// JSL is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program. If not, see <http://www.gnu.org/licenses/>.
// ***************************************************************************
// File created 2009-04-03 17:38:21

/*
Calculate the Levensthein distance (LD) of two strings
Algorithm is taken from http://www.merriampark.com/ld.htm. The algorithm is considered to be public domain.
1
  Set n to be the length of s.
  Set m to be the length of t.
  If n = 0, return m and exit.
  If m = 0, return n and exit.
  Construct a matrix containing 0..m rows and 0..n columns.  
2 
  Initialize the first row to 0..n.
  Initialize the first column to 0..m.
3
  Examine each character of s (i from 1 to n). 
4
  Examine each character of t (j from 1 to m). 
5
  If s[i] equals t[j], the cost is 0.
  If s[i] doesn't equal t[j], the cost is 1. 
6
  Set cell d[i,j] of the matrix equal to the minimum of:
  a. The cell immediately above plus 1: d[i-1,j] + 1.
  b. The cell immediately to the left plus 1: d[i,j-1] + 1.
  c. The cell diagonally above and to the left plus the cost: d[i-1,j-1] + cost.
7
  After the iteration steps (3, 4, 5, 6) are complete, the distance is found in cell d[n,m].
*/
String.prototype.levenshtein=
  function(t) {
    // ith character of s
    var si; 
    // cost
    var c;
    // Step 1
    var n = this.length;
    var m = t.length;
    if (!n)
      return m;
    if (!m)
      return n;
    // Matrix
    var mx = [];
    // Step 2 - Init matrix
    for (var i=0; i<=n; i++) {
      mx[i] = [];
      mx[i][0] = i;
    }
    for (var j=0; j<=m; j++)
      mx[0][j] = j;
    // Step 3 - For each character in this
    for (var i=1; i<=n; i++) {
      si = this.charAt(i - 1);
      // Step 4 - For each character in t do step 5 (si == t.charAt(j - 1) ? 0 : 1) and 6
      for (var j=1; j<=m; j++)
        mx[i][j] = Math.min(mx[i - 1][j] + 1, mx[i][j - 1] + 1, mx[i - 1][j - 1] + (si == t.charAt(j - 1) ? 0 : 1));
    }
    // Step 7
    return mx[n][m];
  };

