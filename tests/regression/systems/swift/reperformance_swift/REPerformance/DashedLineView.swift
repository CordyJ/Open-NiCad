//
//  DashedLineView.swift
//  REPerformance
//
//  Created by Robert Kapizska on 2017-05-26.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import UIKit


@IBDesignable
class DashedLineView: UIView {
	
	@IBInspectable var dashColor: UIColor = .white {
		didSet {
			self.updateColor()
		}
	}
	
	@IBInspectable var lineWidth: CGFloat = 2 {
		didSet {
			self.updateLineWidth()
		}
	}
	
	@IBInspectable var paintedLengthSegment: CGFloat = 9 {
		didSet {
			self.updateLineDashPattern()
		}
	}
	
	@IBInspectable var unpaintedLengthSegment: CGFloat = 6 {
		didSet {
			self.updateLineDashPattern()
		}
	}
	
	override class var layerClass: AnyClass {
		return CAShapeLayer.self
	}
	
	var dashedLayer: CAShapeLayer {
		return self.layer as! CAShapeLayer
	}
	
	
	override func layoutSubviews() {
		super.layoutSubviews()
		
		self.updateSize()
		self.updateLineWidth()
		self.updateLineDashPattern()
		self.updateColor()
	}
	
	func updateSize() {
		let rect = CGRect(x: 0, y: 0, width: self.frame.size.width, height: self.frame.size.height)
		
		self.dashedLayer.bounds = rect
		self.dashedLayer.position = self.center
		self.dashedLayer.lineJoin = CAShapeLayerLineJoin.round
		self.dashedLayer.path = UIBezierPath(roundedRect: rect, cornerRadius: 0).cgPath
	}
	
	func updateColor() {
		self.dashedLayer.strokeColor = self.dashColor.cgColor
	}
	
	func updateLineWidth() {
		self.dashedLayer.lineWidth = self.lineWidth
	}
	
	func updateLineDashPattern() {
		self.dashedLayer.fillColor = UIColor.clear.cgColor
		self.dashedLayer.lineDashPattern = [NSNumber(value: Float(self.paintedLengthSegment)), NSNumber(value: Float(self.unpaintedLengthSegment))]
	}
}
