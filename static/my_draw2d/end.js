draw2d.shape.node.FlowEnd = draw2d.shape.node.FlowCircle.extend({
    NAME:"draw2d.shape.node.FlowEnd",
	init: function(){
		this._super();
		//this.setBackgroundColor("");
		this.createPort("hybrid",new draw2d.layout.locator.InputPortLocator());
	},
	
});