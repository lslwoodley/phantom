// import React, { useState, useEffect, useRef, RefObject } from "react";
// import { Outlet, NavLink, Link } from "react-router-dom";
// import { useTranslation } from "react-i18next";
// import styles from "./Layout.module.css";

// import { useLogin } from "../../authConfig";

// import { LoginButton } from "../../components/LoginButton";
// import { IconButton } from "@fluentui/react";
// import TelemetryDashboard from "../../components/TelemetryDashboard";


// const Layout = () => {
//     const { t } = useTranslation();
//     const [menuOpen, setMenuOpen] = useState(false);
//     const menuRef: RefObject<HTMLDivElement> = useRef(null);

//     const toggleMenu = () => {
//         setMenuOpen(!menuOpen);
//     };

//     const handleClickOutside = (event: MouseEvent) => {
//         if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
//             setMenuOpen(false);
//         }
//     };

//     useEffect(() => {
//         if (menuOpen) {
//             document.addEventListener("mousedown", handleClickOutside);
//         } else {
//             document.removeEventListener("mousedown", handleClickOutside);
//         }
//         return () => {
//             document.removeEventListener("mousedown", handleClickOutside);
//         };
//     }, [menuOpen]);

//     return (
//         <div className={styles.layout}>
//             <header className={styles.header} role={"banner"}>
//                 <div className={styles.headerContainer} ref={menuRef}>
//                     <Link to="/" className={styles.headerTitleContainer}>
//                         <h3 className={styles.headerTitle}>{t("headerTitle")}</h3>
//                     </Link>
//                     <nav>
//                         <ul className={`${styles.headerNavList} ${menuOpen ? styles.show : ""}`}>
//                             <li>
//                                 <NavLink
//                                     to="/"
//                                     className={({ isActive }) => (isActive ? styles.headerNavPageLinkActive : styles.headerNavPageLink)}
//                                     onClick={() => setMenuOpen(false)}
//                                 >
//                                     {t("chat")}
//                                 </NavLink>
//                             </li>
//                             <li>
//     <NavLink
//         to="/qa"
//         className={({ isActive }) =>
//             isActive ? styles.headerNavPageLinkActive : styles.headerNavPageLink
//         }
//         onClick={() => setMenuOpen(false)}
//     >
//         {t("qa")}
//     </NavLink>
// </li>
// <li>
//     <NavLink
//         to="/telemetry"
//         className={({ isActive }) =>
//             isActive ? styles.headerNavPageLinkActive : styles.headerNavPageLink
//         }
//         onClick={() => setMenuOpen(false)}
//     >
//         Telemetry
//     </NavLink>
// </li>

//                         </ul>
//                     </nav>
//                     <div className={styles.loginMenuContainer}>
//                         {useLogin && <LoginButton />}
//                         <IconButton
//                             iconProps={{ iconName: "GlobalNavButton" }}
//                             className={styles.menuToggle}
//                             onClick={toggleMenu}
//                             ariaLabel={t("labels.toggleMenu")}
//                         />
//                     </div>
//                 </div>
//             </header>

//             <Outlet />
//         </div>
//     );
// };

// export default Layout;



// import React, { useState, useEffect, useRef, RefObject } from "react";
// import { Outlet, NavLink, Link } from "react-router-dom";
// import { useTranslation } from "react-i18next";
// import styles from "./Layout.module.css";

// import { useLogin } from "../../authConfig";
// import { LoginButton } from "../../components/LoginButton";
// import { IconButton } from "@fluentui/react";

// const Layout = () => {
//     const { t } = useTranslation();
//     const [menuOpen, setMenuOpen] = useState(false);
//     const menuRef: RefObject<HTMLDivElement> = useRef(null);

//     const toggleMenu = () => {
//         setMenuOpen(!menuOpen);
//     };

//     const handleClickOutside = (event: MouseEvent) => {
//         if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
//             setMenuOpen(false);
//         }
//     };

//     useEffect(() => {
//         if (menuOpen) {
//             document.addEventListener("mousedown", handleClickOutside);
//         } else {
//             document.removeEventListener("mousedown", handleClickOutside);
//         }
//         return () => {
//             document.removeEventListener("mousedown", handleClickOutside);
//         };
//     }, [menuOpen]);

//     return (
//         <div className={styles.layout}>
//             <header className={styles.header} role={"banner"}>
//                 <div className={styles.headerContainer} ref={menuRef}>
//                     <Link to="/" className={styles.headerTitleContainer}>
//                         <h3 className={styles.headerTitle}>{t("headerTitle")}</h3>
//                     </Link>
//                     <nav>
//                         <ul className={`${styles.headerNavList} ${menuOpen ? styles.show : ""}`}>
//                             <li>
//                                 <NavLink
//                                     to="/"
//                                     className={({ isActive }) => (isActive ? styles.headerNavPageLinkActive : styles.headerNavPageLink)}
//                                     onClick={() => setMenuOpen(false)}
//                                 >
//                                     {t("chat")}
//                                 </NavLink>
//                             </li>
//                             <li>
//                                 <NavLink
//                                     to="/qa"
//                                     className={({ isActive }) => (isActive ? styles.headerNavPageLinkActive : styles.headerNavPageLink)}
//                                     onClick={() => setMenuOpen(false)}
//                                 >
//                                     {t("qa")}
//                                 </NavLink>
//                             </li>
//                             <li>
//                                 <NavLink
//                                     to="/telemetry"
//                                     className={({ isActive }) => (isActive ? styles.headerNavPageLinkActive : styles.headerNavPageLink)}
//                                     onClick={() => setMenuOpen(false)}
//                                 >
//                                     Telemetry
//                                 </NavLink>
//                             </li>
//                         </ul>
//                     </nav>
//                     <div className={styles.loginMenuContainer}>
//                         {useLogin && <LoginButton />}
//                         <IconButton
//                             iconProps={{ iconName: "GlobalNavButton" }}
//                             className={styles.menuToggle}
//                             onClick={toggleMenu}
//                             ariaLabel={t("labels.toggleMenu")}
//                         />
//                     </div>
//                 </div>
//             </header>

//             {/* Page outlet rendering child routes */}
//             <Outlet />
//         </div>
//     );
// };

// export default Layout;


// File: frontend/pages/layout/Layout.tsx
import { FC } from 'react';
import styles from './Layout.module.css';
import { LayoutWrapper } from '../../layoutWrapper';
import TelemetryDashboard from '../../components/TelemetryDashboard';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: FC<LayoutProps> = ({ children }) => {
  return (
    <div className={styles.layout}>
      <LayoutWrapper>
        <main className={styles.mainContent}>
          {children}
          <TelemetryDashboard />
        </main>
      </LayoutWrapper>
    </div>
  );
};

export default Layout;
