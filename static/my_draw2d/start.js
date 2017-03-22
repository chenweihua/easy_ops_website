draw2d.shape.node.FlowStart = draw2d.shape.node.FlowCircle.extend({
    NAME:"draw2d.shape.node.FlowStart",
	init: function(){
		this._super();
		this.setBackgroundColor("green");
		this.createPort("hybrid",new draw2d.layout.locator.OutputPortLocator());
	},	
});