$(document).ready(function(){
    templateData    = null;
    pollInterval    = null;
    pollPaused      = false;

    $('#job-alert').bind('hide', function(event){
        resumePolling();
    });

    $('#refresh-toggle-button').click(function(event){
        $(this).find('i').removeClass('icon-pause', false);
        $(this).find('i').removeClass('icon-play', false);
        if( $(this).hasClass('active') )
        {
            stopPolling();
            $(this).find('i').addClass('icon-play');
        } else {
            startPolling();
            $(this).find('i').addClass('icon-pause');
        }
    });

    $('#refresh-button').click(function(event){
        reload();
    });

	reload = function()
	{
        if( pollPaused )
        {
            return;
        }
		$.ajax({
			url: window.api_url_all,
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

        data.jobs.reverse();

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
					} else {
                        data.jobs[i][j]['requeue-button-additional-class']= 'hidden';
                    }

					$('#jobs tbody').append( parseTemplate( $('script[name=job-row]').text(), data.jobs[i][j]) );
				}
			}
		}

        if( templateData == null )
        {
            templateData    = {};
            $('[data-type=template]').each(function(idx,ele){
                templateData[$(ele).attr('id')] = $(ele).html();
            });
        }

        $('a').unbind( '.rqworker_dashboard' );
		$('a[data-role=cancel-job-btn]').bind( 'click.rqworker_dashboard', function(event){
            event.preventDefault();
            cancelJob( $(this).parent().parent().attr('data-job-id') );
        } );

        $('a[data-role=requeue-job-btn]').bind( 'click.rqworker_dashboard', function(event){
            event.preventDefault();
            requeueJob( $(this).parent().parent().attr('data-job-id') );
        } );

        $('a[rel=quick-ajax]').bind('click.rqworker_dashboard', function(event){
            event.preventDefault();
            $.ajax({
                url: $(this).attr('href'),
                dataType: 'json',
                success: function(data, textStatus, jqXHR) {
                    reload();
                }
            });
        });
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

    modalDone = function()
    {

        $('#job-alert').modal().hide();
        $('#job-alert .modal-header button.close').click();
        reload();
    };

    cancelJob = function( id )
    {
        pausePolling();
        $('#job-alert').html( parseTemplate(templateData['job-alert'], {'id': id, 'headline': 'Delete Job', 'question': 'Are you sure you want to delete job'}) );
        $('#job-alert').modal();

        $('#job-alert a[rel=yes]').unbind( '.rqworker_dashboard' );
        $('#job-alert a[rel=yes]').bind('click.rqworker_dashboard', function(event){
            event.preventDefault();
            $.ajax({
                url: window.api_url_job + '/' + id + '/delete',
                dataType: 'json',
                success: modalDone,
                error: modalDone
            });
        });
    };

    requeueJob = function( id )
    {
        pausePolling();
        $('#job-alert').html( parseTemplate(templateData['job-alert'], {'id': id, 'headline': 'Requeue Job', 'question': 'Are you sure you want to requeue job'}) );
        $('#job-alert').modal();

        $('#job-alert a[rel=yes]').unbind( '.rqworker_dashboard' );
        $('#job-alert a[rel=yes]').bind('click.rqworker_dashboard', function(event){
            event.preventDefault();
            $.ajax({
                url: window.api_url_job + '/' + id + '/requeue',
                dataType: 'json',
                success: modalDone,
                error: modalDone
            });
        });
    };

    startPolling = function()
    {
        stopPolling();
        pollInterval    = setInterval( reload, window.poll_interval * 1000 );
        reload();
    };

    stopPolling = function()
    {
        try
        {
            clearInterval(pollInterval);
        } catch(e){}
    };

    pausePolling = function()
    {
        pollPaused  = true;
    };

    resumePolling = function()
    {
        pollPaused  = false;
    };

	reload();
    startPolling();
});