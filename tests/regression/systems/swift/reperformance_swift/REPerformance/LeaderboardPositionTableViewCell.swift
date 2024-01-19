//
//  LeaderboardPositionTableViewCell.swift
//  REPerformance
//
//  Created by Christopher Darc on 2017-05-26.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import UIKit
import AlamofireImage


class LeaderboardPositionTableViewCell: UITableViewCell {
	
	@IBOutlet private var rankLabel: UILabel?
	@IBOutlet private var personImageView: UIImageView?
	@IBOutlet private var nameLabel: UILabel?
	@IBOutlet private var medalImageView: UIImageView?
	@IBOutlet private var rightSideLabel: UILabel?
	@IBOutlet private var isPublicIndicatorView: UIView?
	
	
	override func awakeFromNib() {
		super.awakeFromNib()
		
		self.selectionStyle = .none
		
		self.rankLabel?.textColor = UIColor.white
		self.nameLabel?.textColor = UIColor.white
		self.rightSideLabel?.textColor = UIColor.white
	}
	
	override func prepareForReuse() {
		super.prepareForReuse()
		
		self.rankLabel?.text = nil
		self.nameLabel?.text = nil
		self.rightSideLabel?.text = nil
		self.isPublicIndicatorView?.isHidden = true
		self.medalImageView?.isHidden = true
		
		self.personImageView?.af_cancelImageRequest()
		self.personImageView?.image = nil
	}
	
	
    func configureCell(rankText: String, nameText: String, isPublic: Bool, rightSideText: String, medalVisible: Bool, personFacebookID: String?, profileURL: URL?) {
		self.rankLabel?.text = rankText
		self.nameLabel?.text = nameText
		self.rightSideLabel?.text = rightSideText
		self.medalImageView?.isHidden = (medalVisible == false)
		self.isPublicIndicatorView?.isHidden = (isPublic == false)
		
        if let profileImage = profileURL {
            self.personImageView?.af_setImage(withURL: profileImage, placeholderImage: Asset.Assets.nonFacebook.image)
        }
        else {
            if let imageURL = FacebookImage.imageURLWithFacebookID(personFacebookID) {
                self.personImageView?.af_setImage(withURL: imageURL, placeholderImage: Asset.Assets.nonFacebook.image)
            } else {
                self.personImageView?.image = Asset.Assets.nonFacebook.image
            }
        }
	}
}
