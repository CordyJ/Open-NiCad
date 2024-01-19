//
//  CAGradientLayer+BoltMobile.swift
//  Bolt Mobile
//
//  Created by Christopher Darc on 2017-09-18.
//  Copyright © 2017 Push Interactions. All rights reserved.
//

import UIKit

enum GradientDirection:Int {
    case horizontal
    case diagonal
}

extension CAGradientLayer {
    
    convenience init(frame: CGRect, colors: [UIColor], gradientDirection:GradientDirection) {
        self.init()
        self.frame = frame
        self.colors = []
        for color in colors {
            self.colors?.append(color.cgColor)
        }
        startPoint = CGPoint(x: 0, y: 0)
        switch gradientDirection {
        case .horizontal:
            endPoint = CGPoint(x: 1, y: 0)
        case .diagonal:
            endPoint = CGPoint(x: 1, y: 1)
        }
    }
    
    func createGradientImage() -> UIImage? {
        
        var image: UIImage? = nil
        UIGraphicsBeginImageContext(bounds.size)
        if let context = UIGraphicsGetCurrentContext() {
            render(in: context)
            image = UIGraphicsGetImageFromCurrentImageContext()
        }
        UIGraphicsEndImageContext()
        return image
    }
    
}
