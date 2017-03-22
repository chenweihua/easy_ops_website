draw2d.shape.node.FlowRectangle = draw2d.shape.basic.Rectangle.extend({
	NAME:"draw2d.shape.node.FlowRectangle",
	CNNAME:'任务节点',
	init: function(){
		this._super();
		this.setResizeable(false);
		this.createPort("hybrid",new draw2d.layout.locator.OutputPortLocator());
		this.createPort("hybrid",new draw2d.layout.locator.InputPortLocator());
              
        //this.label = new draw2d.shape.basic.Label({text:"A", color:"#0d0d0d", fontColor:"#0d0d0d"});
        //this.add(this.label, new draw2d.layout.locator.BottomLocator(this));      
        //this.label.installEditor(new draw2d.ui.LabelInplaceEditor());
		//console.log("init",this.getId());
	},
	onContextMenu: function(x,y){
		//console.log("on context menu",this.getId());		
		/*
		此处注意，务必先destroy，再build，否则在canvas中添加多个rect时，
		this的指向会一直指向最初的rect
		*/
		$.contextMenu('destroy','rect'); 		
		$.contextMenu({
			selector: 'rect',
			callback: $.proxy(function(key,options){
				console.log("on callback",this.getId());
				switch(key){
					case 'atom_task':
						$("#id_modal_atom_task").data('current_task',this);
						$("#id_table_atom_task").bootstrapTable('refresh','{silent:true}');
						$("#id_modal_atom_task").modal({backdrop:false,show:true});
						
						break;
                    case 'file':
						$("#id_modal_file").data('current_task',this);
						$("#id_table_file").bootstrapTable('refresh','{silent:true}');
						$("#id_modal_file").modal({backdrop:false,show:true});
						
						break;
                    case 'atom_para':
						$("#id_modal_atom_para").data('current_task',this);
						$("#id_modal_atom_para").modal({backdrop:false,show:true});
						
						break;
					case 'host':
						$("#id_modal_host").data('current_task',this);
						$("#id_table_host").bootstrapTable('refresh','{silent:true}');
						$("#id_modal_host").modal({backdrop:false,show:true});
						
						break;
					default:					
						break;
				}
			},this),
			items: {
				"atom_task": {name: "添加原子任务",},
				"file": {name: "添加文件",},
				"atom_para": {name: "添加参数",},
				"host": {name: "添加设备",},
			},
			x:x,
			y:y,
		});		
	},
});

