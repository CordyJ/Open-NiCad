//
//  ViewControllerBackgroundImage.swift
//
//  Created by Alan Yeung on 2017-04-03.
//  Copyright © 2017 Push Interactions. All rights reserved.
//

import UIKit
import SnapKit


@IBDesignable
class ViewControllerBackgroundImage: NSObject {
	
	private var backgroundImageView: UIImageView?
	
	@IBOutlet private weak var viewController: UIViewController?
	
	@IBInspectable var backgroundImageName: String? {
		didSet {
			if let backgroundImageName = backgroundImageName {
				backgroundImageView?.image = UIImage(named: backgroundImageName)
			}
		}
	}
	
	override func awakeFromNib() {
        
        if backgroundImageView == nil {
            let backgroundImageViewToSet = UIImageView()

            if viewController?.view is UITableView {
                let tableView = viewController?.view as! UITableView
                tableView.backgroundView = backgroundImageViewToSet
            }
            else if viewController?.view is UICollectionView {
                let collectionView = viewController?.view as! UICollectionView
                collectionView.backgroundView = backgroundImageViewToSet
            }
            else {
                if let view = viewController?.view {
                    view.insertSubview(backgroundImageViewToSet, at: 0)
                    backgroundImageViewToSet.snp.makeConstraints({ (make) in
                        make.edges.equalTo(view)
                    })
                }
            }
            backgroundImageView = backgroundImageViewToSet
        }
        
        if let backgroundImageName = backgroundImageName {
            backgroundImageView?.image = UIImage(named: backgroundImageName)
        }
	}
}
