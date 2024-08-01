<h1> Purpose </h1>
<P>This site contains the code and data files associated with the "Hidden in Plain Sight: Antisemitic Content in QAnon subReddits" Article.</p>

<h1> Data </h1>
<P> Following data files are included</P>

<h2> PostIds for the r/greatawakening and r/CBTS_Stream posts that were used in the paper. </h2>
<p>There are two files, one for the submissions (SubmissionIds.csv) - these are original reddit postid the full text cannot be released due to reddit terms and conditions.These were extracted using the PushShift API in March 2023. Some data was missing from the API. </p>

<h3>SubmissionIds.csv:  - these are original reddit post ids</h3>

<P> File format is post_id</P>
  
<h3>CommentsIds.csv - these are the ids for the associated comments </h3>

 <p>File format is post_id,associated_sub_id </p>
  
<h3> CountsByMonth.xlsx - Number of submissions and comments in the above files, by subreddit and month </h3>
  
<h2>Other Supporting Data Files</h2>
<h3>egl.csv</h3> <P>Expert-Generated Dictionary </P>
<h3>hsd.csv</h3><p>Hate-Speech Dictionary</p>
<h3>rollups10.csv</h3><p>Rollup List</p>



<h1> Software </h1>

<h3>data_preprocessing.py</h3><p>Data Preprocessing</p>
<h3>data_preparation.py</h3><p>Data Preparation</p>
<h3>data_analysis.ipynb</h3><p>Data Analysis</p>
<h3>makeCooccurrenceMatrix.py</h3><p>Creating the Coccurrence Matrix </p>
<h3>clusterFromCooccurCSV.py</h3><p>Clustering the Terms </p>
<h3>graphNodesGeneral.py</h3><p>Creating the Network Graph </p>

