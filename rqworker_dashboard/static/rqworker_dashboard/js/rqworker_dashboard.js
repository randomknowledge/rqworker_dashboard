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
                if( data.queues[i]['name'] == "failed" )
                {
                    data.queues[i]['badge-class']   = 'badge-important';
                } else {
                    data.queues[i]['badge-class']   = 'badge-info';
                }
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
                    data.jobs[i][j]['state-label']      = 'pending';
                    data.jobs[i][j]['state-label-class']= 'label-info';
					if( data.jobs[i][j]['ended_at'] )
					{
						data.jobs[i][j]['ended_at']		= toRelative(data.jobs[i][j]['ended_at']);
                        data.jobs[i][j]['state-label']      = 'failed';
                        data.jobs[i][j]['state-label-class']= 'label-important';
					}

					$('#jobs tbody').append( parseTemplate( $('script[name=job-row]').text(), data.jobs[i][j]) );
				}
			}
		}

        $('a[data-role=cancel-job-btn]').unbind( '.rqworker_dashboard' );
		$('a[data-role=cancel-job-btn]').bind( 'click.rqworker_dashboard', function(event){
            cancelJob( $(this).parent().parent().attr('data-job-id') );
        } );
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
		var d = Date.create(universal_date_string);
		return d.relative();
	};

    cancelJob = function( id )
    {
        //doit = window.prompt( '' )
        $('#delete-job-alert').html( parseTemplate($('#delete-job-alert').html(), {'id': id}) );
        $('#delete-job-alert').modal();
    };

	reload();
});