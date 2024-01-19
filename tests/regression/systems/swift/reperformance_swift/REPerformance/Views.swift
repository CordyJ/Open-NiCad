//
//  Views.swift
//  REPerformance
//
//  Created by Christopher Darc on 2017-05-04.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import UIKit


extension UIView {
	
	func roundCornersAndApplyBorder() {
		self.layer.cornerRadius = Constants.UIConstants.CornerRadius
		self.layer.masksToBounds = true
		self.borderWidth = Constants.UIConstants.BorderWidth
		self.borderColor = UIColor.init(named: .rePerformanceOrange)
	}
	
	func addDashedBorder(strokeColor: UIColor, lineWidth: CGFloat) {
		self.layoutIfNeeded()
		
		let shapeLayer = CAShapeLayer()
		let frameSize = self.frame.size
		let shapeRect = CGRect(x: 0, y: 0, width: frameSize.width, height: frameSize.height)
		
		shapeLayer.bounds = shapeRect
		shapeLayer.position = CGPoint(x: (frameSize.width / 2), y: (frameSize.height / 2))
		shapeLayer.fillColor = UIColor.clear.cgColor
		shapeLayer.strokeColor = strokeColor.cgColor
		shapeLayer.lineWidth = lineWidth
		shapeLayer.lineJoin = CAShapeLayerLineJoin.round
		shapeLayer.lineDashPattern = [5, 5]
		shapeLayer.path = UIBezierPath(roundedRect: CGRect(x: 0, y: 0, width: shapeRect.width, height: shapeRect.height), cornerRadius: self.layer.cornerRadius).cgPath
		
		self.layer.addSublayer(shapeLayer)
		self.layer.masksToBounds = true
	}
	
	func addDashline(startView: UIView, endView: UIView, color: UIColor) -> CALayer {
		let line = CAShapeLayer()
		let linePath = UIBezierPath()
		
		// Convert the startPoint to the parentView coord
		let startViewCenter = CGPoint(x: startView.bounds.origin.x + startView.bounds.size.width / 2, y: startView.bounds.origin.y + startView.bounds.size.height / 2)
		let startPoint = startView.convert(startViewCenter, to: self)
		
		let firstPoint = CGPoint(x: self.bounds.width * 0.6, y: startPoint.y)
		
		// Convert the endPoint to the parentView coord
		let endViewCenter = CGPoint(x: endView.bounds.origin.x + endView.bounds.size.width / 2, y: endView.bounds.origin.y + endView.bounds.size.height / 2)
		let endPoint = endView.convert(endViewCenter, to: self)
		
		linePath.move(to: startPoint)
		linePath.addLine(to: firstPoint)
		linePath.addLine(to: endPoint)
		
		line.path = linePath.cgPath
		line.strokeColor = color.cgColor
		line.fillColor = UIColor.clear.cgColor
		line.lineWidth = 1
		line.lineJoin = CAShapeLayerLineJoin.round
		
		self.layer.addSublayer(line)
		
		return line
	}
}
