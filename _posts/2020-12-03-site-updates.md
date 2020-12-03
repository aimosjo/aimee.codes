---
layout: post
title: "Site Updates"
date: 2020-12-03
tags: [projects, jekyll]
---

Here's a list of the most recent updates to the site!
<ul>
  <li>Completely overhauled the site's <code>css</code> based around the responsive top navigation bar, with the classic hamburger drop down mobile menu - thank you to <a href="https://www.youtube.com/watch?v=8QKOaTYvYUA">Kevin Powell</a> for the easy to follow tutorial!</li>
  <li>Reformatted how tables are displayed! In an upcoming post, I work with long and kind of unweildy data summaries and I want a clean way of displaying that for both desktop and mobile users. Using <a href="https://css-tricks.com/responsive-data-tables/">this</a> as my jumping off point, I made the tables easier to view on a mobile device (rows transform into "cards"). By default, only the headers, 2 rows of data, and a link to the full table are displayed to avoid content disruption.
    <br><i>If you want to see the change happen live and you're on the desktop site, try resizing the window under 1000px</i></li>
</ul>

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th class='text'>Feature</th>
      <th class='numeric'>NA Count</th>
      <th class='numeric'>% Missing</th>
      <th class='text'>Data Type</th>
      <th class='text'>Overview</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td data-title='Feature' class='text'>PoolQC</td>
      <td data-title='NA Count' class='numeric'>2909</td>
      <td data-title='% Missing' class='numeric'>0.99657</td>
      <td data-title='Data Type' class='text'>object</td>
      <td data-title='Overview' class='text'>[nan, Ex, Fa, Gd]</td>
    </tr>
    <tr>
      <td data-title='Feature' class='text'>MiscFeature</td>
      <td data-title='NA Count' class='numeric'>2814</td>
      <td data-title='% Missing' class='numeric'>0.96403</td>
      <td data-title='Data Type' class='text'>object</td>
      <td data-title='Overview' class='text'>[nan, Shed, Gar2, Othr, TenC]</td>
    </tr>
  </tbody>
</table>

<a class='read-more-link' href='/assets/missing-values-summary.html'> See full table </a>

<ul>
  <li>Created content pages so when you do access the linked full table, or a plot , the <code>css</code> formatting makes the table easier to read, in both mobile and desktop view</li>
  <li>Changed graphics from <code>.png</code> format to <code>.svg</code> and create multiple <code>@media</code> inquiries in <code>css</code> to determine picture position / scaling for different screen sizes
    <br><i>Note - this only applies to my most recent posts, as I have not yet revisited the graphs generated in Octave from Andrew Ng's Machine Learning course</i></li>
  <li>Now <code>assets/</code> holds ~all~ site assets, including <code>css</code> code, images, html tables, and (now) fonts! Within <code>assets/</code> items are organized on a media type level first, then further divide into specific posts. This might change in the future when the media I use gets significantly more complicated</li>
</ul>

___

<h3>Upcoming Changes</h3>
<ul>
  <li>Create site logo, to be displayed alongside navigation bar</li>
  <li>Update <code>css</code> to shrink top bar on horizontal mobile displays</li>
  <li>Add alt-text and titles to all images</li>
</ul>

___

My next post in the Iowa housing dataset involes both data cleaning and feature engineering. It's been a long time coming, and I'm excited to share what I've been up to! 

Until next time, 祝好！