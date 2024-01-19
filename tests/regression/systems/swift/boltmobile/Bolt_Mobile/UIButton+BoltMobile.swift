//
//  UIButton+BoltMobile.swift
//  Bolt Mobile
//
//  Created by Christopher Darc on 2017-09-21.
//  Copyright © 2017 Push Interactions. All rights reserved.
//

import UIKit

extension UIButton {
    
    func alignImageAndTitleVertically(padding: CGFloat = 6.0) {
        if let imageSize = imageView?.frame.size, let titleSize = titleLabel?.frame.size {
            
            let totalHeight = imageSize.height + titleSize.height + padding
            
            self.imageEdgeInsets = UIEdgeInsets(
                top: -(totalHeight - imageSize.height),
                left: 0,
                bottom: 0,
                right: -titleSize.width
            )
            
            self.titleEdgeInsets = UIEdgeInsets(
                top: 0,
                left: -imageSize.width,
                bottom: -(totalHeight - titleSize.height),
                right: 0
            )
        }
    }
}
