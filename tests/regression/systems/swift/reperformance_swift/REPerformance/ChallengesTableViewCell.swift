//
//  ChallengesTableViewCell.swift
//  REPerformance
//
//  Created by Alan Yeung on 2018-05-28.
//  Copyright © 2018 Push Interactions, Inc. All rights reserved.
//

import UIKit
import AlamofireImage


class ChallengesTableViewCell: UITableViewCell {
	
	@IBOutlet fileprivate var bannerImageView: UIImageView?
	@IBOutlet fileprivate var titleLabel: UILabel?
	@IBOutlet fileprivate var subtitleLabel: UILabel?
	@IBOutlet fileprivate var joinedTotalLabel: UILabel?
	
	
	override func prepareForReuse() {
		super.prepareForReuse()
		
		self.bannerImageView?.image = nil
		self.bannerImageView?.af_cancelImageRequest()
		
		self.titleLabel?.text = nil
		self.subtitleLabel?.text = nil
		self.joinedTotalLabel?.text = nil
	}
	
	
	func configure(challenge: Challenge) {
		self.titleLabel?.text = challenge.name
		self.subtitleLabel?.text = challenge.subtitle
		self.joinedTotalLabel?.text = L10n.challengeTotalJoined("\(challenge.joinedTotal)")
		
		if let bannerImageURL = challenge.imageURL {
			self.bannerImageView?.af_setImage(withURL: bannerImageURL, placeholderImage: UIImage(asset: Asset.Assets.torontoSkylineDELETE))
		}
		else {
			self.bannerImageView?.image = UIImage(asset: Asset.Assets.torontoSkylineDELETE)
		}
	}
}
