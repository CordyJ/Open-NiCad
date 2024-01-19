//
//  ReportCardIndicatorView.swift
//  REPerformance
//
//  Created by Robert Kapizska on 2017-05-03.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import UIKit


@IBDesignable
class ReportCardIndicatorView: UIView {
	
	func commonInit() {
		// NO-OP
	}
	
	override init(frame: CGRect) {
		super.init(frame: frame)
		
		commonInit()
	}
	
	required init?(coder aDecoder:NSCoder) {
		super.init(coder: aDecoder)
		
		commonInit()
	}
	
	override func prepareForInterfaceBuilder() {
		super.prepareForInterfaceBuilder()
		
		commonInit()
	}
	
	
	func addCircleDashedBorder(fillColor: UIColor) {
		self.layoutIfNeeded()
		
		let dottedCircleLayer:CAShapeLayer = CAShapeLayer()
		let frameSize = self.frame.size
		let shapeRect = CGRect(x: 0, y: 0, width: frameSize.width, height: frameSize.height)
		
		dottedCircleLayer.bounds = shapeRect
		dottedCircleLayer.position = CGPoint(x: (frameSize.width / 2), y: (frameSize.height / 2))
		dottedCircleLayer.fillColor = UIColor.clear.cgColor
		dottedCircleLayer.strokeColor = UIColor.white.cgColor
		dottedCircleLayer.lineWidth = 1.0
		
		dottedCircleLayer.lineDashPattern = [3, 3]
		dottedCircleLayer.path = UIBezierPath(roundedRect: CGRect(x: 0, y: 0, width: shapeRect.width, height: shapeRect.height), cornerRadius: self.layer.cornerRadius).cgPath
		
		self.layer.addSublayer(dottedCircleLayer)
		
		let fillCircleLayer = CAShapeLayer()
		let fillFrameSize = CGSize(width: (frameSize.width / 2), height: (frameSize.height / 2))
		let fillShapeRect = CGRect(x: 0, y: 0, width: fillFrameSize.width, height: fillFrameSize.height)
		
		fillCircleLayer.bounds = fillShapeRect
		fillCircleLayer.fillColor = fillColor.cgColor
		fillCircleLayer.position = CGPoint(x: (frameSize.width / 2), y: (frameSize.height / 2))
		fillCircleLayer.path = UIBezierPath(roundedRect: CGRect(x: 0, y: 0, width: fillShapeRect.width, height: fillShapeRect.height), cornerRadius: (self.layer.cornerRadius / 2)).cgPath
		
		self.layer.addSublayer(fillCircleLayer)
	}
}
