$(document).ready(function(){
	reload = function()
	{
		$.ajax({
			url: window.api_url,
			dataType: 'json',
			success: function(data, textStatus, jqXHR) {
				updateAll(data);
			},
			error: function(jqXHR, textStatus, errorThrown) {

			}
		});
	};

	updateAll = function(data)
	{
		$('#queues tbody tr').remove();
		$('#workers tbody tr').remove();
		$('#jobs tbody tr').remove();

		var i;

		if( !data.workers.length )
		{
			$('#workers tbody').append( $('script[name=no-workers-row]').text() );
		} else {
			for( i = 0; i < data.workers.length; i++ )
			{
				$('#workers tbody').append( parseTemplate( $('script[name=worker-row]').text(), data.workers[i]) );
			}
		}

		if( !data.queues.length )
		{
			$('#queues tbody').append( $('script[name=no-queues-row]').text() );
		} else {
			for( i = 0; i < data.queues.length; i++ )
			{
				$('#queues tbody').append( parseTemplate( $('script[name=queue-row]').text(), data.queues[i]) );
			}
		}

		if( !data.jobs.length )
		{
			$('#jobs tbody').append( $('script[name=no-jobs-row]').text() );
		} else {
			for( i = 0; i < data.jobs.length; i++ )
			{
				if( data.jobs[i][0] == undefined )
				{
					data.jobs[i][0]	= data.jobs[i];
				}

				for( var j = 0; j < data.jobs[i].length; j++ )
				{
					data.jobs[i][j]['exc_info_class']	= !data.jobs[i][j]['exc_info'] ? 'hidden' : '';
					data.jobs[i][j]['created_at']		= toRelative(data.jobs[i][j]['created_at']);

					if( data.jobs[i][j]['ended_at'] )
					{
						data.jobs[i][j]['ended_at']		= toRelative(data.jobs[i][j]['ended_at']);
					}

					$('#jobs tbody').append( parseTemplate( $('script[name=job-row]').text(), data.jobs[i][j]) );
				}
			}
		}

		//workers
	};

	parseTemplate = function( tpl, obj )
	{
		var m;
		while( m = tpl.match(/\[\[([a-z0-9_\.\s-]+)\]\]/i) )
		{
			var value;
			try
			{
				value = obj[m[1]];
			} catch( e ) {}
			if( value == undefined )
			{
				value	= '';
			}
			tpl	= tpl.replace( m[0], value );
		}
		return tpl;
	};

	toRelative = function(universal_date_string) {
		var tzo = new Date().getTimezoneOffset();
		var d = Date.create(universal_date_string).rewind({ minutes: tzo });
		return d.relative();
	};

	reload();
});