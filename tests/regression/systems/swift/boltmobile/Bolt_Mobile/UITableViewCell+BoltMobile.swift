//
//  UITableViewCell+BoltMobile.swift
//  Bolt Mobile
//
//  Created by Christopher Darc on 2017-09-22.
//  Copyright © 2017 Push Interactions. All rights reserved.
//

import UIKit

extension UITableViewCell {
    static func defaultCell() -> UITableViewCell {
        let cell = UITableViewCell(style: .default, reuseIdentifier: Constants.UI.DefaultCellIdentifier)
        cell.textLabel?.text = "Error"
        return cell
    }
}
