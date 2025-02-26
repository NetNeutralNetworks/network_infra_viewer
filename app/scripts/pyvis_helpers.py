from bs4 import BeautifulSoup

def parse_py_vis(html):
    soup = BeautifulSoup(html, 'html.parser')
    head = soup.head
    jq = soup.new_tag("script", src="https://ajax.googleapis.com/ajax/libs/jquery/3.7.1/jquery.min.js")
    legend_css = soup.new_tag("link", href="/static/css/overview-legend.css", rel="stylesheet")
    base_css = soup.new_tag("link", href="/static/css/rws.css", rel="stylesheet")
    head.append(jq)
    head.append(base_css)
    head.append(legend_css)
    head_html = head.prettify()
    vis = soup.find('div')
    vis_html = vis.prettify()
    legend = soup.new_tag('div')
    legend['class'] = "legend-panel-container overlay"
    legend_header = soup.new_tag('div')
    legend_header['class'] = "legend-header"
    legend_header.append("Legend")
    legend_body = soup.new_tag('div')
    legend_body['class'] = "legend-body"
    for class_name, description in [('legend-class-purple', 'P - Device'),('legend-class-red', 'PE - Device'),('legend-class-orange', 'CE - Device'),('legend-class-yellow', 'Other'),('legend-class-blue', 'Selected Device')]:
        item = soup.new_tag('div')
        item['class'] = "legend-item"
        icon = soup.new_tag('div')
        icon['class'] = f"legend-icon {class_name}"
        desc = soup.new_tag('div')
        desc['class'] = "legend-description"
        desc.append(description)
        item.append(icon)
        item.append(desc)
        legend_body.append(item)
    legend.append(legend_header)
    legend.append(legend_body)
    script = soup.body.script
    script.append("""
                vis = $('.vis-network'); $('.card').remove(); $('body').append(vis);
                  network.on('doubleClick', function(params){
                    window.location.replace("?hostname=" + nodes.get(params.nodes[0]).label);
                    // alert(nodes.get(params.nodes[0]).label)
                })
                """)
    script_html = script.prettify()
    return head_html+str(legend)+vis_html+script_html