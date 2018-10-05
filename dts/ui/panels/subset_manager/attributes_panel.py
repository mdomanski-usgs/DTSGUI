attributes = '''<!DOCTYPE html>
<html>
<head>
	<meta charset="utf-8">
	<title>Attributes Panel</title>
	<style>
		html, body {
			background: %(bkg_color)s !important;
			font-family: Lucida Grande, Lucida, Arial, sans-serif;
			font-size: 12px;
		}
		div.description {
			float: none;
			width: 100%%;
		}
		div.description * {
			display: inline-block;
			margin-right: 10px;
		}
		div {
			float: left;
			width: 33%%;
		}
		p {
			margin-top: 0;
			margin-bottom: 5px;
		}
		h1 {
			font-size: 14px;
			line-height: 14px;
			margin-top: 0px;
			padding-top: 0px;
			margin-bottom: 10px;
		}
		h2 {
			font-size: 12px;
			margin-bottom: 5px;
			margin-top: 0px;
		}
		.label {
			font-weight: bold;
			padding-right: 8px;
		}
	</style>
	<!--[if lt IE 9]>
	<script src="http://html5shiv.googlecode.com/svn/trunk/html5.js"></script>
	<![endif]-->
	<script src="http://ajax.googleapis.com/ajax/libs/jquery/1.7.2/jquery.min.js"></script>

</head>
<body>
	<h1>%(name)s</h1>
	<div class="description">
		<h2>Description</h2>
		<p>%(description)s</p>
	</div>
	<div>
		<h2>Distance Along Cable</h2>
		<p><span class="label">Start:</span>%(x_min)s</p>
		<p><span class="label">End:</span>%(x_max)s</p>
		<p><span class="label">Length:</span>%(x_delta)s</p>
	</div>
	<div>
		<h2>Time Range</h2>
		<p><span class="label">Start:</span>%(t_min)s</p>
		<p><span class="label">End:</span>%(t_max)s</p>
		<p><span class="label">Duration:</span>%(t_delta)s</p>
	</div>
	<div>
		<h2>Temperature Statistics</h2>
		<p><span class="label">Min:</span>%(min)s</p>
		<p><span class="label">Max:</span>%(max)s</p>
		<p><span class="label">Mean:</span>%(mean)s</p>
		<p><span class="label">Std Deviation:</span>%(std)s</p>
	</div>
 
</body>
</html>'''