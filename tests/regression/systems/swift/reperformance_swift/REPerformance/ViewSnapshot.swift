//
//  ViewSnapshot.swift
//  REPerformance
//
//  Created by Robert Kapizska on 2017-05-10.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import UIKit


extension UIView {
	
	func snapshot(backgroundColor: UIColor = UIColor.clear) -> UIImage? {
		let renderer = UIGraphicsImageRenderer(bounds: self.bounds)
		let image = renderer.image { rendererContext in
			backgroundColor.setFill()
			rendererContext.fill(rendererContext.format.bounds)
			self.layer.render(in: rendererContext.cgContext)
		}
		
		return image
	}
}
