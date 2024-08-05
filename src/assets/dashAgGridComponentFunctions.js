var dagcomponentfuncs = (window.dashAgGridComponentFunctions = window.dashAgGridComponentFunctions || {});

dagcomponentfuncs.Link = function (props) {
    var link = props.data.link;

    return React.createElement(
        'a',
        {
            href: link,
            target: '_blank',
            style: {textDecoration: 'none'}
        },
        props.value
    );
};